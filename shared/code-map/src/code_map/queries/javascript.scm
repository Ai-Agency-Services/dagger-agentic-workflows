# JavaScript Tree-sitter query for symbol and import extraction

; functions
(function_declaration name: (identifier) @name) @function
(function_expression name: (identifier) @name) @function

; classes
(class_declaration name: (identifier) @name) @class

; methods
(method_definition name: (property_identifier) @name) @method

; top-level variables
(lexical_declaration (variable_declarator name: (identifier) @name)) @var
(var_declaration (variable_declarator name: (identifier) @name)) @var

; imports: import ... from 'source'
(import_declaration source: (string) @source) @import
