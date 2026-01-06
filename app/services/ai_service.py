"""
SMBPilot AI Agent Service using LangGraph.
This service creates and manages the AI agent that handles SMB operations.
"""
import os
import inspect
from typing import TypedDict, Annotated, Sequence, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger("smbpilot_agent")


class AgentState(TypedDict):
    """State of the SMBPilot agent"""
    messages: Sequence[Dict[str, Any]]
    user_id: int
    tenant_id: int
    user_info: Dict[str, Any]
    tenant_info: Dict[str, Any]
    db: Any  # AsyncSession


class SMBPilotAgent:
    """
    SMBPilot AI Agent - Specialized for SMB operations.
    Uses LangGraph for stateful conversation and tool execution.
    """
    
    def __init__(self):
        """Initialize the SMBPilot agent"""
        # Initialize LLM based on provider
        if settings.AI_PROVIDER == "anthropic":
            self.llm = ChatAnthropic(
                model="claude-3-5-sonnet-20241022",
                temperature=0.7,
                anthropic_api_key=settings.ANTHROPIC_API_KEY
            )
        else:
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.7,
                openai_api_key=settings.OPENAI_API_KEY
            )
        
        # Initialize tools (will be set during runtime with db context)
        self.tools = []
        self.tool_implementations = {}  # Map wrapper names to actual functions
        self.tool_executor = None
        
        # Build the graph
        self.graph = None
        
    def _create_system_prompt(self, user_info: Dict[str, Any], tenant_info: Dict[str, Any]) -> str:
        """Create a context-aware system prompt"""
        return f"""You are SMBPilot, an expert AI assistant specialized in small and medium business (SMB) operations and management.

        **Current Context:**
        - User: {user_info.get('full_name', 'User')} ({user_info.get('email', 'unknown')})
        - Organization: {tenant_info.get('name', 'Unknown')}
        - Your Role: {tenant_info.get('role', 'member')}

        **Your Capabilities:**
        You can help with ALL business operations including:
        - Creating, updating, listing, and deleting businesses
        - Managing organizations/tenants
        - Viewing and switching between organizations
        - Setting primary organization for quick access

        **Your Personality:**
        - Professional but friendly and conversational
        - Proactive - suggest next steps and improvements
        - Efficient - complete tasks in fewest steps possible
        - Clear - always confirm actions before executing destructive operations (deletes)

        **Guidelines:**
        1. Always execute actions directly - don't just describe what you would do
        2. When user asks to create/update/delete, use the appropriate tools immediately
        3. Provide clear confirmations after completing actions
        4. If information is missing, ask specific questions
        5. For ambiguous requests, make reasonable assumptions but mention them
        6. After completing a task, suggest relevant next steps
        7. IMPORTANT: Once you receive a successful tool result, DO NOT call the same tool again. Use the result to answer the user.
        8. CRITICAL: If a tool returns success=True, consider the task COMPLETE and respond to the user immediately.

        **Examples of what you can do:**
        - "Create a restaurant business called Joe's Pizza" → Use create_business tool ONCE, then confirm
        - "Show me all my businesses" → Use list_businesses tool ONCE, then show results
        - "Update the phone number for Joe's Pizza" → Use update_business tool ONCE, then confirm
        - "Delete the business with ID abc-123" → Confirm first, then use delete_business tool ONCE
        - "Switch to my other organization" → Use list_tenants and set_primary_tenant tools, then confirm
        - "What's my organization?" → Use get_current_tenant ONCE, then tell the user

        Remember: You have FULL access to execute these operations. Call each tool ONLY ONCE per user request, then respond with the results!
        """
    
    async def _call_model(self, state: AgentState) -> AgentState:
        """Call the language model with current state"""
        messages = state["messages"]
        user_info = state["user_info"]
        tenant_info = state["tenant_info"]
        
        # Create system message with context
        system_prompt = self._create_system_prompt(user_info, tenant_info)
        
        # Convert messages to LangChain format
        lc_messages = [SystemMessage(content=system_prompt)]
        
        for msg in messages:
            if msg["role"] == "user":
                lc_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                lc_messages.append(AIMessage(content=msg["content"]))
        
        # Bind tools to the model
        llm_with_tools = self.llm.bind_tools(self.tools)
        
        # Call the model
        response = await llm_with_tools.ainvoke(lc_messages)
        
        # Add response to messages
        state["messages"].append({
            "role": "assistant",
            "content": response.content,
            "tool_calls": response.tool_calls if hasattr(response, 'tool_calls') else []
        })
        
        return state
    
    async def _execute_tools(self, state: AgentState) -> AgentState:
        """Execute tools called by the model"""
        last_message = state["messages"][-1]
        tool_calls = last_message.get("tool_calls", [])
        
        if not tool_calls:
            return state
        
        # Execute each tool
        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"].copy()  # Copy to avoid modifying original
            
            logger.info(f"Executing tool: {tool_name} with args: {list(tool_args.keys())}")
            
            # Get the actual implementation function
            impl_func = self.tool_implementations.get(tool_name)
            
            if not impl_func:
                logger.error(f"No implementation found for tool: {tool_name}")
                state["messages"].append({
                    "role": "function",
                    "name": tool_name,
                    "content": f"Error: Tool {tool_name} not found"
                })
                continue
            
            try:
                # Check which parameters the function actually accepts
                sig = inspect.signature(impl_func)
                param_names = set(sig.parameters.keys())
                
                logger.info(f"Function {tool_name} accepts: {param_names}")
                
                # Filter tool_args to only include parameters the function accepts
                filtered_args = {k: v for k, v in tool_args.items() if k in param_names}
                
                # Inject required parameters if missing
                if "db" in param_names and "db" not in filtered_args:
                    filtered_args["db"] = state["db"]
                if "user_id" in param_names and "user_id" not in filtered_args:
                    filtered_args["user_id"] = state["user_id"]
                if "tenant_id" in param_names and "tenant_id" not in filtered_args:
                    filtered_args["tenant_id"] = state["tenant_id"]
                
                logger.info(f"Calling {tool_name} with filtered args: {list(filtered_args.keys())}")
                
                # Call the actual implementation function
                result = await impl_func(**filtered_args)
                
                logger.info(f"Tool {tool_name} succeeded: {str(result)[:100]}")
                
                # Add tool result to messages
                state["messages"].append({
                    "role": "function",
                    "name": tool_name,
                    "content": str(result)
                })
            except Exception as e:
                logger.error(f"Tool execution error in {tool_name}: {str(e)}", exc_info=True)
                state["messages"].append({
                    "role": "function",
                    "name": tool_name,
                    "content": f"Error: {str(e)}"
                })
        
        return state
    
    def _should_continue(self, state: AgentState) -> str:
        """Determine if we should continue or end"""
        last_message = state["messages"][-1]
        
        # If last message has tool calls, execute them
        if last_message.get("tool_calls"):
            return "continue"
        
        # Otherwise, we're done
        return "end"
    
    def build_graph(self, tools: list, tool_implementations: dict = None):
        """Build the LangGraph workflow"""
        self.tools = tools
        self.tool_implementations = tool_implementations or {}
        
        # Create the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("agent", self._call_model)
        workflow.add_node("tools", self._execute_tools)
        
        # Set entry point
        workflow.set_entry_point("agent")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools",
                "end": END
            }
        )
        
        # Add edge from tools back to agent
        workflow.add_edge("tools", "agent")
        
        # Compile the graph
        self.graph = workflow.compile()
        
        return self.graph
    
    async def chat(
        self,
        message: str,
        user_id: int,
        tenant_id: int,
        user_info: Dict[str, Any],
        tenant_info: Dict[str, Any],
        conversation_history: list,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Process a chat message and return response.
        
        Args:
            message: User's message
            user_id: Current user ID
            tenant_id: Current tenant ID
            user_info: User information dict
            tenant_info: Tenant information dict
            conversation_history: Previous messages in conversation
            db: Database session
        
        Returns:
            Dictionary with response and metadata
        """
        if not self.graph:
            raise RuntimeError("Graph not built. Call build_graph() first.")
        
        # Prepare initial state
        initial_state: AgentState = {
            "messages": conversation_history + [{"role": "user", "content": message}],
            "user_id": user_id,
            "tenant_id": tenant_id,
            "user_info": user_info,
            "tenant_info": tenant_info,
            "db": db
        }
        
        try:
            # Run the graph with increased recursion limit
            final_state = await self.graph.ainvoke(
                initial_state,
                config={"recursion_limit": 100}
            )
            
            # Extract the assistant's response
            assistant_messages = [
                msg for msg in final_state["messages"]
                if msg["role"] == "assistant"
            ]
            
            if assistant_messages:
                last_response = assistant_messages[-1]["content"]
            else:
                last_response = "I'm sorry, I couldn't process that request."
            
            return {
                "response": last_response,
                "conversation_history": final_state["messages"],
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Agent chat error: {str(e)}")
            return {
                "response": f"I encountered an error: {str(e)}",
                "conversation_history": conversation_history,
                "success": False,
                "error": str(e)
            }
