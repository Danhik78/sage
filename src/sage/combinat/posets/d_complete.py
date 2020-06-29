# ****************************************************************************
#       Copyright (C) 2020 Stefan Grosser <stefan.grosser1@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  https://www.gnu.org/licenses/
# ****************************************************************************

from sage.combinat.posets.posets import Poset, FinitePoset
from sage.misc.lazy_attribute import lazy_attribute

class DCompletePoset(FinitePoset):
    r"""
    D-complete posets are a class of posets introduced by Proctor in [Proc1999].
    It includes common families such as shapes, shifted shapes, and rooted forests. Proctor showed in [PDynk1999]
    that d-complete posets have decompositions in ``irreducible`` posets, and showed in [Proc2014] that
    d-complete posets admit a hook-length formula (see [HLF]). A complete proof of the hook-length formula
    can be found in [KY2019].
  
    EXAMPLES::

        sage: from sage.combinat.posets.poset_examples import Posets
        sage: P = Posets.DoubleTailedDiamond(2)
        sage: type(P)
        <class 'sage.combinat.posets.d_complete.DCompletePoset_with_category'>

    The additional internal data structure consists of:

    - the hook lengths of the elements of the poset

        sage: P._hooks
        {1: 1, 2: 2, 3: 3, 4: 3, 5: 4, 6: 5}

    TESTS::

        sage: TestSuite(P).run()

    See also the other tests in the class documentation.
    """

    def _repr_(self):
        r"""
        TESTS::

            sage: from sage.combinat.posets.d_complete import DCompletePoset
            sage: P = DCompletePoset(DiGraph({0: [1], 0: [2], 1: [3], 2: [3], 3: []}))
            sage: P._repr_()
            'Finite d-complete poset containing 4 elements'
        """
        s = "Finite d-complete poset containing %s elements" % self._hasse_diagram.order()
        if self._with_linear_extension:
            s += " with distinguished linear extension"
        return s


    @lazy_attribute
    def _hooks(self):
        r"""
        The hook lengths of the elements of the d-complete poset. For the definition 
        of hook lengths for d-complete posets, see [KY2019].

        TESTS::

            sage: from sage.combinat.posets.d_complete import DCompletePoset
            sage: P = DCompletePoset(DiGraph({0: [1, 2], 1: [3], 2: [3], 3: []}))
            sage: P._hooks
            {0: 1, 1: 2, 2: 2, 3: 3}
            sage: from sage.combinat.posets.poset_examples import Posets
            sage: P = DCompletePoset(Posets.YoungDiagramPoset(Partition([3,2,1]))._hasse_diagram.reverse()) 
            sage: P._hooks
            {0: 5, 1: 3, 2: 1, 3: 3, 4: 1, 5: 1}
        """
        from collections import deque
        hooks = {}

        min_diamond = {} # Maps max of double-tailed diamond to min of double-tailed diamond
        max_diamond = {} # Maps min of double-tailed diamond to max of double-tailed diamond

        diamonds = self.diamonds() # Tuples of four elements that are diamonds
        
        diamond_index = {} # Map max elmt of double tailed diamond to index of diamond

        # Find all the double-tailed diamonds and map the mins and maxes. 
        for index, d in enumerate(diamonds):
            min_diamond[d[3]] = d[0]
            max_diamond[d[0]] = d[3]
            diamond_index[d[3]] = index

            min_elmt = d[0]
            max_elmt = d[3]

            while True:
                potential_min = self.lower_covers(min_elmt)
                
                potential_max = self.upper_covers(max_elmt)

                # Check if any of these make a longer double tailed diamond
                found_diamond = False
                for (mn, mx) in [(i,j) for i in potential_min for j in potential_max]:
                    if len(self.lower_covers(mx)) != 1:
                        continue
                    if len(self._hasse_diagram.all_paths(self._element_to_vertex(mn), self._element_to_vertex(mx))) == 2:
                        # Success
                        min_elmt = mn
                        max_elmt = mx

                        min_diamond[mx] = mn
                        max_diamond[mn] = mx
                        diamond_index[mx] = index
                        found_diamond = True
                        break
                if not found_diamond:
                    break

        # Compute the hooks
        queue = deque(self.minimal_elements())
        enqueued = set()
        while queue:
            elmt = queue.popleft()
            
            if elmt not in diamond_index:
                hooks[elmt] = self.order_ideal_cardinality([elmt])
            else:
                diamond = diamonds[diamond_index[elmt]]
                side1 = diamond[1]
                side2 = diamond[2]
                hooks[elmt] = hooks[side1] + hooks[side2] - hooks[min_diamond[elmt]]
            enqueued.add(elmt)

            for c in self.upper_covers(elmt):
                if c not in enqueued:
                    queue.append(c)
                    enqueued.add(c)

        return hooks
                
    def get_hook(self, elmt):
        r"""
        Get the hook length of a specific element.

        TESTS::

            sage: from sage.combinat.posets.d_complete import DCompletePoset
            sage: P = DCompletePoset(DiGraph({0: [1], 1: [2]}))
            sage: P.get_hook(1)
            2
        """
        return self._hooks[elmt]

    def get_hooks(self):
        """
        Get all the hook lengths returned in a dictionary
        
        TESTS::

            sage: from sage.combinat.posets.d_complete import DCompletePoset
            sage: P = DCompletePoset(DiGraph({0: [1, 2], 1: [3], 2: [3], 3: []}))
            sage: P.get_hooks()
            {0: 1, 1: 2, 2: 2, 3: 3}
            sage: from sage.combinat.posets.poset_examples import Posets
            sage: P = DCompletePoset(Posets.YoungDiagramPoset(Partition([3,2,1]))._hasse_diagram.reverse()) 
            sage: P.get_hooks()
            {0: 5, 1: 3, 2: 1, 3: 3, 4: 1, 5: 1}

        """
        return dict(self._hooks)

    @staticmethod
    def is_d_complete(cls, poset):
        """
        Check if a poset is d-complete
        """
        pass

    def linear_extensions(self, facade=False):
        r"""
        Return the enumerated set of all the linear extensions of this poset with hook lengths.

        INPUT:

        - ``facade`` -- a boolean (default: ``False``);
          whether to return the linear extensions as plain lists

        EXAMPLES::

            sage: from sage.combinat.posets.d_complete import DCompletePoset
            sage: P = DCompletePoset(DiGraph({0: [1, 2], 1: [3], 2: [3], 3: [4]}))
            sage: L = P.linear_extensions()
            sage: L.cardinality()
            2
            sage: L.list()
            [[0, 1, 2, 3, 4], [0, 2, 1, 3, 4]]

        TESTS::

            sage: from sage.combinat.posets.d_complete import DCompletePoset
            sage: from sage.combinat.posets.poset_examples import Posets
            sage: P = DCompletePoset(Posets.YoungDiagramPoset(Partition([3,2,1]))._hasse_diagram.reverse()) 
            sage: L = P.linear_extensions()
            sage: L.cardinality()
            16
            sage: L.list()
            [[5, 4, 3, 2, 1, 0],
             [4, 5, 3, 2, 1, 0],
             [4, 5, 2, 3, 1, 0],
             [4, 2, 5, 3, 1, 0],
             [2, 4, 5, 3, 1, 0],
             [2, 4, 5, 1, 3, 0],
             [2, 4, 1, 5, 3, 0],
             [4, 2, 1, 5, 3, 0],
             [4, 2, 5, 1, 3, 0],
             [4, 5, 2, 1, 3, 0],
             [5, 4, 2, 1, 3, 0],
             [5, 2, 4, 1, 3, 0],
             [2, 5, 4, 1, 3, 0],
             [2, 5, 4, 3, 1, 0],
             [5, 2, 4, 3, 1, 0],
             [5, 4, 2, 3, 1, 0]]
        """
        from .linear_extensions import LinearExtensionsOfPosetWithHooks
        return LinearExtensionsOfPosetWithHooks(self, facade=facade)
    