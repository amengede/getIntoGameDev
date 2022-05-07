//enable strict mode
"use strict";

function main(){
    var canvas = document.getElementById("mainCanvas")
    var gl = canvas.getContext("webgl2"); //gl is a context, but can be referenced like an object
    if (!gl){
        return;
    }

    //create shaders, link program
    var vertexShaderSource = `#version 300 es
    
    in vec2 vertex_position;
    in vec3 vertex_color;

    out vec3 fragment_color;

    void main() {
        gl_Position = vec4(vertex_position, 0, 1);
        fragment_color = vertex_color;
    }
    `;

    var fragmentShaderSource = `#version 300 es
    
    precision highp float;

    in vec3 fragment_color;

    out vec4 outColor;

    void main() {
        outColor = vec4(fragment_color, 1);
    }
    `;

    var vertexShader = createShader(gl, gl.VERTEX_SHADER, vertexShaderSource);
    var fragmentShader = createShader(gl, gl.FRAGMENT_SHADER, fragmentShaderSource);
    var shader = createProgram(gl, vertexShader, fragmentShader);

    //declare triangle data
    //x, y, r, g, b
    gl.useProgram(shader);
    var vertexData = [
        -0.5, 0.5, 1, 0, 0,
         0.5, 0.5, 0, 1, 0,
         0,  -0.5, 0, 0, 1
    ];
    var vertexCount = 3;
    var vao = gl.createVertexArray();
    gl.bindVertexArray(vao);
    var vbo = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, vbo);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(vertexData), gl.STATIC_DRAW);
    //attribute pointers
    //position
    gl.enableVertexAttribArray(gl.getAttribLocation(shader, "vertex_position"));
    //location, size, data type, normalize, stride, offset
    gl.vertexAttribPointer(gl.getAttribLocation(shader, "vertex_position"), 2, gl.FLOAT, false, 20, 0);
    //color
    gl.enableVertexAttribArray(gl.getAttribLocation(shader, "vertex_color"));
    gl.vertexAttribPointer(gl.getAttribLocation(shader, "vertex_color"), 3, gl.FLOAT, false, 20, 8);

    //declare viewport
    gl.viewport(0, 0, gl.canvas.width, gl.canvas.height);

    //draw
    gl.useProgram(shader);
    gl.clearColor(0.5, 0, 0.25, 1);
    gl.clear(gl.COLOR_BUFFER_BIT);

    gl.bindVertexArray(vao);
    gl.drawArrays(gl.TRIANGLES, 0, vertexCount);
}

function createShader(gl, type, source){
    var shader = gl.createShader(type);
    gl.shaderSource(shader, source);
    gl.compileShader(shader);
    var success = gl.getShaderParameter(shader, gl.COMPILE_STATUS);
    if(success){
        return shader;
    }

    //error
    console.log(gl.getShaderInfoLog(shader));
    gl.deleteShader(shader);
    return undefined;
}

function createProgram(gl, vertexShader, fragmentShader){
    var program = gl.createProgram();
    gl.attachShader(program, vertexShader);
    gl.attachShader(program, fragmentShader);
    gl.linkProgram(program);
    var success = gl.getProgramParameter(program, gl.LINK_STATUS);
    if (success){
        return program;
    }

    //error
    console.log(gl.getProgramInfoLog(program));
    gl.deleteProgram(program);
    return undefined;
}

main();