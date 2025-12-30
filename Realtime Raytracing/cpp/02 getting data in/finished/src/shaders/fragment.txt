#version 330 core

in vec2 fragmentTexCoord;

uniform sampler2D colorBuffer;

out vec4 color;

void main()
{
    color = texture(colorBuffer, fragmentTexCoord);
}