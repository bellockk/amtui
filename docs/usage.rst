=====
Usage
=====

To use Artifact Management Tool User Interface in a project::

    amt gui

Artifact trees are a hierarchical data structure consisting of the following node types.

String
  String nodes in the tree are simple strings and are the "leafs" of the tree.  These strings can contain templating information to be rendered when requested.

List
  List nodes contain an array of any other node type.

Dictionary
  Dictionary nodes contain a map of keys to nodes of any other node type.

Any node type can be a file or a node within an existing file.  Dictionary nodes can be a directory or file, or a node within an exiting directory or file.

Any branch of of the node tree can have at most one node of file type.

