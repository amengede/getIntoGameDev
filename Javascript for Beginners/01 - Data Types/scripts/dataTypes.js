console.log("Hello world! I am using JavaScript!");

/*
    Data Types:

    Numbers: int, float, double are all included
    64 bit number
*/

//operations
console.log(3.5 + 2);
console.log(3.5 - 2);
console.log(3.5 * 2);
console.log(3.5 / 2);
console.log(3.5 ** 2);
console.log(8 % 3);

//special cases, sentinel values
console.log(3.5 / 0);
console.log(-3.5 / 0);
console.log(0/0);
console.log(Infinity - Infinity);

//strings
console.log('Hello world! \
I am using JavaScript!');
console.log(`Hello world! 
I am using JavaScript!`);
//literal template
console.log(`one divided by zero is ${1/0}`);
//concatenate
console.log("This " + "is" + " " + "a long string.");

//typeof
console.log(typeof 3.5);
console.log(typeof "hi");
console.log(typeof `one divided by zero is ${1/0}`);
console.log(typeof Infinity);
console.log(typeof NaN);

//comparison <, > , <=, ...
console.log(`three is less than 4: ${3 < 4}`);
console.log(NaN == NaN);
console.log(0/0 == Infinity - Infinity);

//logic
console.log("logic\n")
console.log(true && true);
console.log(true && false);
console.log(typeof (true && 0));
// 5 = 0101
// 2 = 0010
// bitwise and: 5 & 2 = 0000
console.log(5 & 2);
// or: |, ||