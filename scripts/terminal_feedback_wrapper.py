#!/usr/bin/env python3
"""
Terminal Feedback Wrapper for Dagger Agent Interactions

This script wraps Dagger agent function calls and facilitates user feedback
when agents request it. The loop exits when user hits Ctrl+C twice.
"""

import sys
import signal
import time
import subprocess
import argparse
from typing import List, Optional


class FeedbackHandler:
    def __init__(self):
        self.ctrl_count = 0
        self.last_ctrl_time = 0
        self.should_exit = False
        self.agent_process: Optional[subprocess.Popen] = None
        
        # Set up signal handler
        signal.signal(signal.SIGINT, self.handle_sigint)
    
    def handle_sigint(self, signum, frame):
        """Handle Ctrl+C presses - single stops agent, double exits"""
        current_time = time.time()
        
        if current_time - self.last_ctrl_time < 2.0:  # Within 2 seconds
            self.ctrl_count += 1
            if self.ctrl_count >= 2:
                print("\n🔴 Exiting feedback loop...")
                self.should_exit = True
                if self.agent_process:
                    self.agent_process.terminate()
                sys.exit(0)
        else:
            self.ctrl_count = 1
        
        self.last_ctrl_time = current_time
        
        if self.agent_process and self.agent_process.poll() is None:
            print("\n⏹️  Stopping agent... (Press Ctrl+C again within 2 seconds to exit)")
            self.agent_process.terminate()
        else:
            print("\n⏹️  Press Ctrl+C again within 2 seconds to exit the feedback loop")
    
    def run_agent_with_feedback(self, dagger_command: List[str]) -> None:
        """Run the Dagger agent command and handle feedback requests"""
        print(f"🚀 Starting agent: {' '.join(dagger_command)}")
        
        try:
            # Run the Dagger command once with bidirectional communication
            print("\n" + "="*60)
            print("🤖 AGENT RUNNING")
            print("="*60)
            
            self.agent_process = subprocess.Popen(
                dagger_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Continuously stream output and handle feedback
            while not self.should_exit:
                if self.agent_process.poll() is not None:
                    # Process has ended
                    return_code = self.agent_process.returncode
                    if return_code == 0:
                        print("\n✅ Agent completed successfully!")
                    else:
                        print(f"\n❌ Agent failed with return code: {return_code}")
                    break
                
                try:
                    output = self.agent_process.stdout.readline()
                    if output == '':
                        # No more output, process might be done or waiting
                        time.sleep(0.1)
                        continue
                        
                    print(output.rstrip())
                    
                    # Check if agent is requesting feedback
                    if self.needs_feedback(output):
                        self.collect_and_send_feedback()
                        
                except Exception as e:
                    print(f"\n❌ Error reading output: {e}")
                    break
                    
        except KeyboardInterrupt:
            # This will be handled by our signal handler
            pass
        except Exception as e:
            print(f"\n❌ Error running agent: {e}")
        finally:
            if self.agent_process and self.agent_process.poll() is None:
                self.agent_process.terminate()
                try:
                    self.agent_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.agent_process.kill()
        
        print("\n🏁 Feedback session ended")
    
    def needs_feedback(self, output: str) -> bool:
        """Check if the agent output indicates a feedback request"""
        feedback_indicators = [
            "feedback requested",
            "waiting for feedback", 
            "review and approve",
            "user input required",
            "press enter to continue",
            "what would you like to do",
            "please provide",
            "do you want to"
        ]
        
        output_lower = output.lower()
        return any(indicator in output_lower for indicator in feedback_indicators)
    
    def collect_and_send_feedback(self) -> None:
        """Collect feedback from the user and send it to the agent"""
        print("\n" + "="*60)
        print("💬 FEEDBACK REQUESTED")
        print("="*60)
        print("The agent is waiting for your input.")
        print("Type your response and press Enter.")
        print("Press Ctrl+C twice to exit the feedback loop.")
        print("-" * 60)
        
        try:
            user_input = input("Your response: ").strip()
            
            if user_input and self.agent_process and self.agent_process.poll() is None:
                print(f"\n📝 Sending to agent: {user_input}")
                # Send feedback to the running agent
                self.agent_process.stdin.write(user_input + '\n')
                self.agent_process.stdin.flush()
            else:
                print("\n⏭️  Continuing without feedback...")
                # Send empty line to continue
                if self.agent_process and self.agent_process.poll() is None:
                    self.agent_process.stdin.write('\n')
                    self.agent_process.stdin.flush()
                
        except (EOFError, KeyboardInterrupt):
            # Handle Ctrl+D or Ctrl+C during input
            print("\n⏭️  Feedback cancelled...")
        except BrokenPipeError:
            print("\n❌ Agent process has ended, cannot send feedback")


def main():
    parser = argparse.ArgumentParser(
        description="Terminal feedback wrapper for Dagger agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/terminal_feedback_wrapper.py dagger call --mod agents/codebuff orchestrate-feature-development --feature-task-description "Add user profiles"
  
  python scripts/terminal_feedback_wrapper.py dagger call --mod services/neo test-connection
"""
    )
    
    parser.add_argument(
        'command',
        nargs='+',
        help='The dagger command and arguments to execute'
    )
    
    args = parser.parse_args()
    
    print("🎯 Terminal Feedback Wrapper for Dagger Agents")
    print("================================================")
    print("• Single Ctrl+C: Stop current agent")
    print("• Double Ctrl+C: Exit feedback loop")
    print("• The agent will naturally ask for feedback when needed")
    print()
    
    handler = FeedbackHandler()
    handler.run_agent_with_feedback(args.command)


if __name__ == "__main__":
    main()
