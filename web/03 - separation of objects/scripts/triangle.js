class Triangle{
    constructor(gl,shader,position,size,color){
        this.gl = gl;
        this.shader = shader;
        gl.useProgram(shader);
        this.vertexData = [
            -size[0]/2 + position[0], size[1]/2 + position[1], color[0], color[1], color[2],
            size[0]/2 + position[0], size[1]/2 + position[1], color[0], color[1], color[2],
            position[0],  -size[1]/2 + position[1], color[0], color[1], color[2]
        ];
        this.vertexCount = 3;
        this.vao = gl.createVertexArray();
        gl.bindVertexArray(this.vao);
        this.vbo = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, this.vbo);
        gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(this.vertexData), gl.STATIC_DRAW);
        //attribute pointers
        //position
        gl.enableVertexAttribArray(gl.getAttribLocation(shader, "vertex_position"));
        //location, size, data type, normalize, stride, offset
        gl.vertexAttribPointer(gl.getAttribLocation(shader, "vertex_position"), 2, gl.FLOAT, false, 20, 0);
        //color
        gl.enableVertexAttribArray(gl.getAttribLocation(shader, "vertex_color"));
        gl.vertexAttribPointer(gl.getAttribLocation(shader, "vertex_color"), 3, gl.FLOAT, false, 20, 8);
    }

    draw(){
        this.gl.useProgram(this.shader);
        this.gl.bindVertexArray(this.vao);
        this.gl.drawArrays(this.gl.TRIANGLES, 0, this.vertexCount);
    }
}