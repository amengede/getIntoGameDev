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

    //declare triangles
    var triangle1 = new Triangle(gl, shader, [0,0], [0.5, 0.75], [1.0, 1.0, 0.0]);
    var triangle2 = new Triangle(gl, shader, [-0.5,0.2], [0.25, 0.375], [0.0, 1.0, 1.0]);

    //declare viewport
    gl.viewport(0, 0, gl.canvas.width, gl.canvas.height);

    //draw
    gl.useProgram(shader);
    gl.clearColor(0.5, 0, 0.25, 1);
    gl.clear(gl.COLOR_BUFFER_BIT);

    triangle1.draw();
    triangle2.draw();
}

main();