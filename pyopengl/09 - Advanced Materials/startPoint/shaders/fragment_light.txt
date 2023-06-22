#version 330 core

in vec2 fragmentTexCoord;

uniform sampler2D imageTexture;
uniform vec3 tint;

out vec4 color;

void main()
{
    color = vec4(tint, 1) * texture(imageTexture, fragmentTexCoord);
}