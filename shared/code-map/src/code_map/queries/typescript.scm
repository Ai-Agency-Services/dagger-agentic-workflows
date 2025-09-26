# TypeScript Tree-sitter query for symbol and import extraction

; functions
(function_declaration name: (identifier) @name) @function

; classes
(class_declaration name: (identifier) @name) @class

; methods
(method_signature name: (property_identifier) @name) @method
(method_definition name: (property_identifier) @name) @method

; variables
(lexical_declaration (variable_declarator name: (identifier) @name)) @var

; imports
(import_declaration source: (string) @source) @import
