let test = 0.3;
console.log(test);
const number = Number(prompt("How many terms would you like to use to approximate pi?"));
//console.log(`${number} was entered`);
/*
let num1 = number;
num1 += 1;
console.log(`num1 is now ${num1}`);
*/
if(!Number.isNaN(number)){
    //approximate pi
    let piApprox = 0;
    for (let i = 0; i < number; i++) {
        piApprox += (-1)**i * 4 / (2*i + 1);
        // 4/1 - 4/3 + 4/5 - 4/7 + ...
    }

    //log result
    console.log(`pi, approximated to ${number} terms is ${piApprox}`);
    let error = piApprox - Math.PI;
    let errorType;
    if (error > 0){
        errorType = "overestimated";
    }
    else if (error < 0) {
        errorType = "underestimated";
    }
    else {
        errorType = "were perfectly correct";
    }
    console.log("We " + errorType + ` by ${Math.abs(error)}`);
}
else{
    //declare error
    console.log("You didn't enter a number! Refresh and try again.");
}