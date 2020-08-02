Immutable collections for Python
====================================

Immutable.py provides many Persistent Immutable data structures based on
[Immutable.js][], focusing on both mimicking Immutable.js' API and feeling
pythonic. Immutable.py includes `List`.

[Immutable][] data cannot be changed once created, leading to much simpler
application development, no defensive copying, and enabling advanced memoization
and change detection techniques with simple logic. [Persistent][] data presents
a mutative API which does not update the data in-place, but instead always
yields new updated data.

These data structures aim to be highly efficient on cPython by using structural
sharing via [hash maps tries][] and [vector tries][] as popularized by Clojure
and Scala, minimizing the need to copy or cache data.

[Immutable.js]: https://github.com/immutable-js/immutable-js
[Persistent]: http://en.wikipedia.org/wiki/Persistent_data_structure
[Immutable]: http://en.wikipedia.org/wiki/Immutable_object
[hash maps tries]: http://en.wikipedia.org/wiki/Hash_array_mapped_trie
[vector tries]: http://hypirion.com/musings/understanding-persistent-vector-pt-1
