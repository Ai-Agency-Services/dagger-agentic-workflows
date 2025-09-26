# Python Tree-sitter query for symbol and import extraction

; functions
(function_definition name: (identifier) @name) @function

; classes
(class_definition name: (identifier) @name) @class

; imports (import x)
(import_statement name: (dotted_name (identifier) @module)) @import
; imports (from x import y)
(import_from_statement module_name: (dotted_name (identifier) @module)) @import_from

