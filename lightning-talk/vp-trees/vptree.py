'''
vptree.py

This data structure was implemented and documented by Jochen Spieker, who has done fantastic
work implementing and documenting several metric tree structures in Python, which you can
find here: http://well-adjusted.de/~jrspieker/mspace/. I changed a couple small bits, but
99.9 percent of the work is his.

You can see another simpler implementation here, which might make the intuition behind
the algorithm a bit more clear: http://www.logarithmic.net/pfh/blog/01164790008

More information can be found on Wikipedia: http://en.wikipedia.org/wiki/Vantage-point_tree
'''

import sys, random, weakref, string
from operator import itemgetter

DIST_CTR = 0 

class UnindexableObjectError(Exception): 
    """ 
 
    This Exception is thrown when the call to the distance function in 
    use by a metric space throws an exception. This should not happen 
    during regular usage and is a hint that either your distance 
    function is buggy or you tried to index objects which your distance 
    function cannot handle. 
 
    """ 
 
    def __init__(self, msg, e): 
        self.orig_exception = e 
        Exception.__init__(self, msg) 
 
    orig_exception = None 
    """ The exception that has triggered this exception.  """ 
 
    pass 

class MetricTree(object):
    def __init__(self, objects=None, func=None, parent=None): 
        """ 
 
        Create a new metric tree. If ``objects`` and ``func`` are given, 
        the given objects will be indexed immediately using the distance 
        function which makes it possible to immediately start so search 
        for other objects in it. Otherwise, you have to call `construct` 
        later in order to make use of this metric tree. 
 
        """ 
        self._values = list() 
        self._size = 0 
        self._height = 1 
        self._func = func 
        self.parent = parent 
        self._num_nodes = 0 
        self._incr_node_counter() 
        self._calculate_height() 
        if objects and func: 
            self.construct(objects, func) 
 
    def range_search(self, obj, min_dist=0, max_dist=0): 
        """ 
 
        Return a list of all objects in this subtree whose distance to 
        `obj` is at least `min_dist` and at most `max_dist`.  `min_dist` 
        and `max_dist` have to satisfy the condition ``0 <= min_dist <= 
        max_dist``. 
 
        If this metric tree is empty, an empty list is returned, 
        regardless of whether this tree has been previously constructed 
        or not. 
 
        If calling the distance function fails for any reason, 
        `UnindexableObjectError` will be raised. 
 
        """ 
        assert( 0 <= min_dist <= max_dist ) 
        if not self: return list() 
        result, candidates = list(), [self]
        while candidates: 
            node = candidates.pop() 
            distance = node._get_dist(obj) 
            if min_dist <= distance <= max_dist: 
                result.extend([(v, distance) for v in node._values]) 
            candidates.extend( node._get_child_candidates( 
                distance, min_dist, max_dist)) 
        return sorted(result , key=itemgetter(1))
 
    def search(self, obj, max_dist): 
        """ 
 
        Equivalent to range_search(obj, min_dist=0, max_dist). 
 
        """ 
        return self.range_search(obj, max_dist=max_dist) 
 
    def _get_child_candidates(self, distance, min_dist, max_dist): 
        """ 
 
        Return a sequence of child nodes that may contain objects with a 
        distance difference between (inclusive) ``min`` and ``max`` to a 
        certain query object.  Note that the query object is *not* 
        passed to this method.  Instead, ``distance`` is the query 
        object's previously calculated distance to this node. 
 
        """ 
        raise NotImplementedError() 
 
    def construct(self, objects, func): 
        """ 
 
        (Re)Index this space with the given ``objects`` using the 
        distance function ``func``.  Previous contents will be 
        discarded.  ``objects`` has to be a sequence or an iterable. The 
        distance function ``func`` needs to be applicable to all objects 
        contained in ``objects``. 
 
        If calling the distance function fails for any reason, 
        `UnindexableObjectError` will be raised. 
 
        """ 
        raise NotImplementedError() 
 
    def insert(self, obj): 
        """ 
 
        Insert a single object into the metric tree.  Returns ``self``, 
        i.e. the tree itself. 
 
        This method may not be implemented by all subclasses of 
        `MetricTree` since not all data structures allow to do this 
        efficiently.  `NotImplementedError` will be raised when this is 
        the case. 
 
        If calling the distance function fails for any reason, 
        `UnindexableObjectError` will be raised. 
 
        """ 
        raise NotImplementedError() 
 
    def is_root(self): 
        """ 
 
        Answer whether this node is the root of a tree (i.e. it has no 
        parent). 
 
        """ 
        return self.parent is None 
 
    def is_leaf(self): 
        """ 
 
        Answer whether this node is a leaf node (i.e. it has no 
        children) 
 
        """ 
        return not self.children 
 
    def __children(self): 
        """ 
 
        A sequence of this node's children. 
 
        The possible number of children per node is 
        implementation-dependent. Leaf nodes return an empty sequence. 
 
        """ 
        raise NotImplementedError() 
    children = property(__children) 
 
    def __num_nodes(self): 
        """ 
 
        The number of nodes in this tree. 
 
        This may be different from the number of objects contained in 
        this tree in cases where two or more of these objects are 
        considered equal by the distance function in use (i.e., for two 
        objects ``p`` and ``q``, calling ``self._func(p, q)`` returns 
        ``0`` and when the tree is empty, i.e. there is one node (the 
        root node) but it doesn't contain any values. 
 
        """ 
        return self._num_nodes 
    num_nodes = property(__num_nodes) 
 
 
    def __height(self): 
        """ 
 
        The height of this tree. 
 
        Empty trees have a height of ``0``, trees containing one or more 
        objects have a height ``>= 1``. 
 
        """ 
        return self._height 
    height = property(__height) 
 
    def __parent(self): 
        """ 
 
        The parent of this node. `None` if this node is the root 
        of a tree. 
 
        """ 
        return self._parent 
 
    def __set_parent(self, parent): 
        """ 
 
        Set the parent of this node. 
 
        Parent references are stored as "weak references" to avoid 
        circular references which the garbage collector cannot dissolve 
        by itself. 
 
        """ 
        if parent is None: 
            self._parent = None 
        else: 
            # the callback ensures that the weakref is deleted 
            # as soon as the parent node disappears so that this 
            # node recognizes it is the new root. 
            callback = lambda proxy: self.__set_parent(None) 
            self._parent = weakref.proxy(parent, callback) 
 
    parent = property(__parent, __set_parent) 
 
    def _incr_size(self, incr=1): 
        """ 
 
        Increment the size counter for this node and all its parents 
        recursively. 
 
        Should be called whenever an object is inserted into the tree. 
 
        """ 
        def f(node, incr=incr): node._size += incr 
        self._apply_upwards(f) 
 
    def _calculate_height(self, recursive=True): 
        """ 
 
        Set this node's height to one and (if `recursive` is `True`) 
        propagate this change upwards in the tree. 
 
        """ 
        self._height = height = 1 
        if recursive: 
            node = self.parent 
            while node is not None: 
                height += 1 
                if node._height < height: 
                    node._height = height 
                    node = node.parent 
                else: 
                    node = None 
 
    def _incr_node_counter(self, incr=1): 
        """ 
 
        Increment the node counter for this node and all its parents 
        recursively. 
 
        Should be called whenever a new child of this node is created. 
 
        """ 
        def f(node, incr=incr): node._num_nodes += incr 
        self._apply_upwards(f) 
 
    def _apply_upwards(self, func, **args): 
        """ 
 
        Helper method to apply a function to this node and all its 
        parents recursively. The given function must accept one node as 
        the first parameter and may accept arbitrary keyword parameters 
        as well. 
 
        """ 
        node = self 
        func(node, **args) 
        while not node.is_root(): 
            node = node.parent 
            func(node, **args) 
 
    def _get_dist(self, obj): 
        """ 
 
        Apply this node's distance function to the given object and one 
        of this node's values. 
 
        Raises `UnindexableObjectError` when distance computation fails. 
 
        """ 
        global DIST_CTR
        try: 
            distance = self._func(self._values[0], obj) 
            DIST_CTR += 1 
        except IndexError, e: 
            sys.stderr.write("Node is empty, cannot calculate distance!\n") 
            raise e 
        except Exception, e: 
            raise UnindexableObjectError(e, "Cannot calculate distance" 
                    + " between objects %s and %s using %s" \
                        % (self._values[0], obj, self._func)) 
        return distance 
 
    def __iter__(self): 
        """ 
 
        A generator that yields all objects in this node and its 
        children by doing recursive pre-order traversal. Implementors 
        might choose to use another traversal method which better suits 
        their data structure. 
 
        Note that objects are returned in no specific order. 
 
        This implementation will always return objects in the same order 
        as long as the tree's content does not change and the 
        implementation of `children` always returns the children in the 
        same order. If `children` is not implemented at all, 
        `NotImplementedError` will be raised. 
 
        """ 
        for obj in self._values: 
            yield obj 
        for child in self.children: 
            for obj in child: 
                yield obj 
 
    itervalues = __iter__ 
 
    def iternodes(self): 
        """ 
 
        A generator that yields all nodes in this subtree by doing 
        recursive pre-order traversal. Implementors might choose to use 
        another traversal method which better suits their data 
        structure. 
 
        Note that objects are returned unordered. 
 
        This implementation will always return nodes in the same order 
        as long as the tree's content does not change and the 
        implementation of `children` always returns the children in the 
        same order. If `children` is not implemented at all, 
        `NotImplementedError` will be raised. 
 
        """ 
        yield self 
        for child in self.children: 
            for node in child.iternodes(): 
                yield node 
 
    def __nonzero__(self): 
        """ 
 
        Return True if this node contains any objects. 
 
        """ 
        return len(self._values) > 0 
 
    def __len__(self): 
        """ 
 
        Return the number of objects in this subtree 
 
        """ 
        return self._size 
 
    def __contains__(self, item): 
        """ 
 
        Search for objects with a distance of zero to `item` and return 
        True if something is found, otherwise False. 
 
        Note that this does **not** check for object identity! Instead, 
        the definition of equality is delegated to the distance function 
        in use. 
 
        """ 
        return len(self.range_search(item)) > 0 
 
    def __repr__(self): 
        if self: 
            return str(self.__class__) + ": " + str(self._values[0]) 
        else: 
            return "<empty node>" 


class VPTree(MetricTree): 
    def __init__(self, objects=None, func=None, parent=None): 
        self._median = None 
        self._leftchild = None 
        self._rightchild = None 
        super(VPTree, self).__init__(objects, func, parent) 
 
    def construct(self, objects, func): 
        self._func = func 
        if objects: 
            if self.is_root(): 
                # when building the root of the tree, we make sure `objects` 
                # is a shuffled list to improve VP picking and make 
                # decomposing easier. 
                objects = list(objects) 
                #random.shuffle(objects) 
            self._values = [self._pick_VP(objects)] 
            left, right = self._decompose(objects) 
            del objects # we don't need that list anymore so release it 
                        # before doing recursive calls 
            self._incr_size(len(self._values)) 
            if left: 
                self._leftchild = VPTree(left, func, self) 
            if right: 
                self._rightchild = VPTree(right, func, self) 
        return self 
 
    def _pick_VP(self, objects): 
        # this probably makes no sense whatsoever, simply pop()ing would 
        # do just as well, I guess. Need to think about good strategies. 
        if len(objects) > 15: 
            sample = objects[:5] 
            max_diff = -1 
            vp = None 
            for o in sample:
                dists = [ self._func(other, o) for other in sample 
                          if other is not o]
                #if not dists: return vp
                diff = max(dists) - min(dists)
                if diff > max_diff: 
                    max_diff, vp = diff, o 
            objects.remove(vp) 
            return vp 
        else: 
            return objects.pop() 
 
    def _decompose(self, objects): 
        """ 
 
        Perform the process called "ball decomposition" by Peter 
        Yianilos. 
 
        `objects` has to be an iterable that yields objects applicable 
        to the metric function in use. The return value is a tuple of 
        two lists: one list that contains all elements having a distance 
        smaller than the median distance to this node's value, the 
        second list contains all objects whose distance is equal to or 
        larger than the median distance of all given `objects` to this 
        node's value. 
 
        """ 
        dist_per_obj = list() 
        for obj in objects: 
            distance = self._get_dist(obj) 
            if distance == 0: 
                self._values.append(obj) 
            else: 
                dist_per_obj.append( (distance, obj) ) 
        if dist_per_obj: 
            self._median = VPTree.determine_median(zip(*dist_per_obj)[0]) 
            left  = [ obj for dist, obj in dist_per_obj 
                      if dist < self._median ] 
            right = [ obj for dist, obj in dist_per_obj  
                      if dist >= self._median ] 
        else: 
            left, right = None, None 
        return left, right 
 
    @staticmethod 
    def determine_median(numbers): 
        """ 
 
        Determine the median from a sequence of numbers (or anything 
        else that can be ``sorted()``). 
 
        This does not use an optimal ``O(n)`` algorithm but instead 
        relies on CPython's speed when sorting (``O(n log(n))``). 
 
        """ 
        return sorted(numbers)[ len(numbers) / 2  ] 
 
    def _get_child_candidates(self, distance, min_dist, max_dist): 
        if self._leftchild and distance - max_dist < self._median: 
            yield self._leftchild 
        if self._rightchild and distance + max_dist >= self._median: 
            yield self._rightchild 
 
    def __children(self): 
        return [child for child in (self._leftchild, self._rightchild) 
                if child] 
    children = property(__children)