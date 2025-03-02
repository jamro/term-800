from src.ai.Conversation import Conversation


class ExecGuardian(Conversation):

    def __init__(self, api_key, settings, model_name="gpt-4o-mini", token_stats=None):
        system_message = """
          You are a cybersecurity expert specializing in Linux system security. Your task is to analyze a given shell command and determine if it is risky.

          A command is considered **risky** if it falls into any of the following categories:
          - **Destructive Commands**: Deletes, overwrites, or corrupts files (e.g., `rm -rf /`, `dd if=/dev/zero of=/dev/sda`).
          - **Privileged Commands**: Requires `sudo` or modifies system settings (e.g., `sudo chmod 777 /etc/passwd`).
          - **Network & Remote Access Risks**: Alters SSH, firewall, or network configurations (e.g., `iptables -F`, `sudo ufw disable`).
          - **Process & System Disruption**: Kills critical processes or shuts down the system (e.g., `kill -9 1`, `shutdown -h now`).
          - **Unexpected Command Combinations**: Dangerous use of pipes (`|`), `&&`, or command substitutions (e.g., `rm -rf $(find / -name "*.log")`).
          - **SSH Connection Breaking**: Commands that terminate or disrupt an active SSH session (e.g., `pkill -u $USER`, `kill -9 $$`).

          ### **Instructions:**
          1. If the command is **risky**, respond with: [one-sentence explanation of why it is dangerous]
          2. If the command is **safe**, respond with: 'SAFE'
          
          - Do **not** provide any additional information.
        """
        super().__init__(api_key, model_name, system_message, token_stats)
        self.settings = settings
        self.confirm_execution = lambda command, reason: True

    def is_safe(self, command):
        if self.settings.get("guard") == "off":
            return "SAFE"
        if self.settings.get("guard") == "on":
            return "Guardian in ON. All commands must be confirmed."

        response = self.ask(f"Command to Analyze: '{command}'")

        return response.strip()

    def is_allowed(self, command):
        msg = self.is_safe(command)
        if msg == "SAFE":
            return True

        return self.confirm_execution(command, msg)
