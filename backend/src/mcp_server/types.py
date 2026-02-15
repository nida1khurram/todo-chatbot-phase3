"""
Types for the MCP server
"""
class TextContent:
    def __init__(self, type=None, text=None):
        self.type = type
        self.text = text