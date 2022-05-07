console.log(square(5));

function square(x) {
    return x * x;
}

const square2 = function(x) {
    return x * x;
};

console.log(square2(6));

let square3 = function(x) {
    return x * x;
};

square3 = function(x) {
    return x * x * x;
};

console.log(square3(8));

let square4 = x => x * x;

console.log(square4(8));

let generalPower = (x,y) => x ** y;

console.log(generalPower(2,3));

let generalPower2 = (x,y) => {
    let result = 1;
    let power = 0;

    while (power < y) {
        result *= x;
        power++;
    }

    return result;
}

console.log(generalPower(4,3));

function power(y) {
    return x => x ** y;
}

let square5 = power(2);
console.log(square5(11));

let f = x => Math.sin(x) + x;

function binarySearch(a,b,f,target) {
    let eps = 0.001;
    let midpoint = (a + b) / 2;
    let guess = f(midpoint);
    let error = Math.abs(target - guess);
    //base case
    if (error < eps) {
        return midpoint;
    }

    if ((target - f(a)) * (target - f(midpoint)) < 0) {
        return binarySearch(a, midpoint, f, target);
    }
    return binarySearch(midpoint, b, f, target);
}

console.log(binarySearch(0,6,f,4));