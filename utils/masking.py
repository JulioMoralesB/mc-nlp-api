import re

def mask_ip_in_text(text: str) -> str:
    """
    Masks the IP addresses in the given text for logging purposes.
    """
    ip_pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
    return re.sub(ip_pattern, lambda match: mask_ip(match.group(0)), text)

def mask_ip(ip: str) -> str:
    """
    Masks the IP address for logging purposes.
    """
    parts = ip.split('.')
    if len(parts) == 4:
        return f"{parts[0]}.****.***.{parts[3]}"
    return ip