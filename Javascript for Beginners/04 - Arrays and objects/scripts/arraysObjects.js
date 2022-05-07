let list = [1, 4, 9, 16];
console.log(list);
console.log(list[3]);
console.log(list.length);
list.push(25);
console.log(list);
console.log(list.pop());
console.log(list.shift());
console.log(list);

let player1 = {
    playing: true,
    points: 12,
    items: ["gocart", "golf club"]
};

console.log(player1);
console.log(JSON.stringify(player1));

console.log("gameOver" in player1);
console.log(Object.keys(player1));
Object.assign(player1, {playing:false, gameOver:true});
console.log(player1);

let points = [
    {x:0,y:0},
    {x:3,y:93}
];

let obj1 = {x:1};
let obj2 = obj1;
console.log(obj1 == obj2);
let obj3 = {x:1};
console.log(obj1 == obj3);

const obj4 = {y:10};
obj4.y = 12;
//obj4 = {y:24};
//Object.assign(obj4, {x=3});

let players = [];

function registerPlayer(playing, points, items){
    players.push({playing, points, items});
}

registerPlayer(true, 34, ["baseball bat", "black cat"]);
registerPlayer(false, 23, ["radar"]);
console.log(players);

function calculatePoints(players){
    for (let player of players){
        let pts = 0;
        for (let item of player.items) {
            pts += item.length;
        }
        player.points = pts;
    }
}

calculatePoints(players);
console.log(players);