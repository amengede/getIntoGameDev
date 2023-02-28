#version 330 core

in vec3 rayDirection;

uniform samplerCube imageTexture;

out vec4 color;

void main()
{
    color = texture(imageTexture, rayDirection);
}