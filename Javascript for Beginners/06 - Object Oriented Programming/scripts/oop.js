class weight{
    constructor(massKG){
        this.kilos = massKG;
    }

    get pounds() {
        return this.kilos / 0.454;
    }

    set pounds(p) {
        this.kilos = p * 0.454;
    }

    static fromPounds(p) {
        return new weight(0.454 * p);
    }
}

mass1 = new weight(3);
console.log(mass1.kilos);
console.log(mass1.pounds);

mass1.pounds = 5;
console.log(mass1.kilos);
console.log(mass1.pounds);

mass2 = weight.fromPounds(10);
console.log(mass2.kilos);
console.log(mass2.pounds);