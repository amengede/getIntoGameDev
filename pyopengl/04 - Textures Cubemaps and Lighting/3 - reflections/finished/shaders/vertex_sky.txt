#version 330 core

layout (location=0) in vec2 vertexPos;

uniform vec3 camera_forwards;
uniform vec3 camera_right;
uniform vec3 camera_up;

out vec3 rayDirection;

void main()
{
    gl_Position = vec4(vertexPos, 0.0, 1.0);
    rayDirection = camera_forwards + vertexPos.x * camera_right + vertexPos.y * camera_up;
}