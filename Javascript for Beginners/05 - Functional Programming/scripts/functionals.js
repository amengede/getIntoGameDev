let numbers = [1,2,3,4,5,6,7,8,9,10];
let dataset = [
    {
        carat:0.23, cut:"ideal", price:326
    },
    {
        carat:0.21, cut:"premium", price:326
    },
    {
        carat:0.23, cut:"good", price:327
    },
    {
        carat:0.29, cut:"premium", price:334
    },
    {
        carat:0.31, cut:"good", price:335
    },
    {
        carat:0.24, cut:"very good", price:336
    },
    {
        carat:0.24, cut:"very good", price:336
    },
    {
        carat:0.26, cut:"very good", price:337
    },
    {
        carat:0.22, cut:"fair", price:337
    },
    {
        carat:0.23, cut:"very good", price:338
    }];

/*
    map x => f(x)
*/
function map(array, f) {
    let result = [];
    for (element of array) {
        result.push(f(element));
    }
    return result;
}

console.log(map(numbers, x => x * x));
console.log(numbers.map(x => x * x));

/*
    filter
*/
function filter(array, test) {
    let passed = [];
    for (let element of array) {
        if (test(element)) {
            passed.push(element);
        }
    }
    return passed;
}

console.log(filter(numbers, x => x % 2 == 0));
console.log(numbers.filter(x => x%2 == 0));

/*
    reduce - crunch array down to single number
*/
function reduce(array, f, accumulator) {
    let result = accumulator;
    for (let element of array){
        result = f(result, element);
    }
    return result;
}

console.log(reduce(numbers, (x,y) => x + y, 0));
console.log(numbers.reduce((x,y) => x+y));

function average(array) {
    return array.reduce((x,y)=>x+y) / array.length;
}

console.log(average(numbers));

console.log(average(dataset.filter(d=>d.cut=="very good").map(d=>d.price)));