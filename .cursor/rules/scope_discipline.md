# Strict Scope Discipline

Rule to ensure that code changes are strictly limited to what was explicitly requested, avoiding scope creep.

<rule>
name: scope_discipline
description: Enforce strict adherence to requested scope of changes, preventing feature creep or unnecessary modifications

filters:
  - type: event
    pattern: "pre_suggestion"

actions:
  - type: modify_suggestion
    transformer: |
      # This transformer ensures that responses follow scope discipline
      
      def enforce_scope_discipline(suggestion):
          # Add explicit scope reminder header to the assistant's planning
          scoped_suggestion = "SCOPE REMINDER: Implement ONLY what was explicitly requested. Make minimal necessary changes.\n\n" + suggestion
          
          # Add implementation guidelines
          guidelines = """
          Scope Implementation Checklist:
          1. Identify the specific request/task
          2. Determine minimum required changes to fulfill the request
          3. Ignore potential improvements outside explicit requirements
          4. Do not add unrelated features or enhancements
          5. Do not modify code unrelated to the request
          6. Do not add extra logging/debugging beyond what was requested
          7. Preserve existing style and patterns unless change was requested
          """
          
          # Insert guidelines at appropriate position
          if "```" in suggestion:
              # If there's code, insert before first code block
              parts = suggestion.split("```", 1)
              scoped_suggestion = parts[0] + guidelines + "\n\n```" + parts[1]
          else:
              # Otherwise add at the beginning
              scoped_suggestion = guidelines + "\n\n" + suggestion
              
          return scoped_suggestion

      return enforce_scope_discipline(suggestion)

  - type: suggest
    message: |
      Your request will be implemented with strict scope discipline:
      - Only implementing exactly what you asked for
      - Making minimal necessary changes
      - Not expanding scope with additional features
      - Preserving existing patterns/style unless changes requested

examples:
  - input: |
      # User request to add a validation function
      "Add input validation to the login form"
    output: |
      # The AI will ONLY add validation to the login form, without:
      # - Changing the form UI/styling
      # - Adding additional security features not requested
      # - Refactoring existing code
      # - Adding logging/debugging
      # - Changing error handling beyond validation 

  - input: |
      # User request to fix a specific bug
      "Fix the calculation error in the total price function"
    output: |
      # The AI will ONLY fix the specific calculation error, without:
      # - Optimizing other parts of the function
      # - Adding additional validation or error handling
      # - Refactoring surrounding code
      # - Adding extra features
      # - Changing function interfaces

metadata:
  priority: high
  version: 1.0
</rule>