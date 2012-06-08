/** A set of "functional programming" tools for Javascript.
 *
 * @author Jefferson Heard, <jefferson.r.heard@gmail.com>
 *
 * @version 1.0
 */

/**
 * Iterate over the (owned) properties of an object or the items of an array.
 *
 * @param obj - an array or object
 * @param fun - a function expecting the value of the property or array cell.
 *
 * @return nothing
 */
function iter(obj, fun) {
    for(var v in obj) { if(obj.hasOwnProperty(v)) {
        fun(obj[v]);
    }}
}

/**
 * Iterate over the owned properties of an object or the items of the array, with indexes.
 *
 * @param obj - an array or object
 * @param fun - a function that expects parameters (key_or_index, value)
 *
 * @return nothing
 */
function enumerate(obj, fun) {
    for(var v in obj) { if(obj.hasOwnProperty(v)) {
        fun(v, obj[v]);
    }}
}

/**
 * Iterate over the (owned) properties of an object or the items of an array and return an array of the results.
 *
 * @param obj - an array or object
 * @param fun - a function that expects the value and returns a new value
 * @return {Array} of the results of fun(value)
 */
function mapping(obj, fun) {
    var ret = [];
    for(var v in obj) { if(obj.hasOwnProperty(v)) {
        ret.push(fun(obj[v]));
    }}
    return ret;
}

function filter(obj, fun) {
    var ret=[];
    for(var v in obj) {
        if(fun(obj[v])) {
            ret.push(obj[v]);
        }
    }
    return ret;
}


/**
 * Iterate over the (owned) properties of an object or the items of an array and return an array of the results.
 *
 * @param obj - an array or object
 * @param fun - a function that expects the value and returns a new value
 * @return {object} of the results of fun(value), one per key.
 */
function enummap(obj, fun) {
    var ret = {};
    for(var v in obj) { if(obj.hasOwnProperty(v)) {
        ret[v] = fun(v, obj[v]);
    }}
    return ret;
}
function keyset(obj) {
    return enummap(obj, function() {return true;} );
}

function values(obj, fun) {
    return mapping(obj, function(v) { return v; });
}

function keys(obj, fun) {
    return enumap(obj, function(k, v) { return k; });
}
/**
 * Iterate over the owned properties of an object or the items of the array and come out with a single value.
 *
 * @param obj - an array or object
 * @param initial - the initial value to "seed" the reduction with.
 * @param fun - a function that expects (accum, object) -> new_accum
 * @return {*} - the result of repetitively doing accum <- fun(initial, o) for each o in obj
 */
function reduce(obj, initial, fun) {
    var ret = initial;
    for(var v in obj) { if(obj.hasOwnProperty(v)) {
        ret = fun(ret, obj);
    }}
    return ret;
}

/**
 * Iterate over two arrays and return an object with the left array as the keys and the right array as the values.
 *
 * @param left - an array of strings
 * @param right - an array of objects
 * @return {Object} - a object of { left[i]: right[i] };
 */
function zip(left, right) {
    var i, ret;
    var n = left.length > right.length ? right.length : left.length;
    ret = {};
    for(i=0; i<n; i++) {
        ret[left[i]] = right[i];
    }
    return ret;
}

/**
 *
 */
function noop() {}

/**
 * If an object has a property, return the value of that property, otherwise return a default value.
 *
 * @param obj
 * @param property
 * @param dflt
 * @return {*}
 */
function either(obj, property, dflt) {
    return obj.hasOwnProperty(property) ? obj[property] : dflt;
}

/**
 * Lisp-like anaphoric if
 *
 * @param test
 * @param success
 * @param fail
 * @return {*}
 */
function aif(test, success, fail) {
    if(test) {
        return success(test);
    }
    else {
        return fail();
    }
}

/**
 * Merge two objects / dictionaries
 *
 * @param base
 * @param dest
 * @return {*}
 */
function merge(base, dest) {
    var ret = $.extend({}, base);
    return $.extend(ret, dest);
}

function mergeLeft(base, dest) {
    var ret = $.extend({}, dest);
    return $.extend(ret, base);
}

/**
 * Merge two sorted lists
 *
 * @param l1
 * @param l2
 * @param key - the sort key
 * @return {Array}
 */
function sift(l1, l2, key) {// merge two sorted lists
    var ret = [];
    var i = 0;
    var j = 0;
    var k1 = l1.length > 0 ? key(l1[0]) : null;
    var k2 = l2.length > 0 ? key(l2[0]) : null;

    while(i < l1.length && j < l2.length) {
         if(k1 <= k2) {
             ret.push(k1);
             i++;
         }
         else {
             ret.push(k2);
             j++;
         }
    }

    if(i < l1.length) {
        ret = ret.concat(l1.slice(i));
    }
    if(j < l2.length) {
        ret = ret.concat(l2.slice(j));
    }

    return ret;
}
