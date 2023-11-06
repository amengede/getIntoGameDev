#version 330 core

out vec2 fragmentTexCoord;

const vec2[6] positions = vec2[](
    vec2( 1.0,  1.0),
    vec2(-1.0,  1.0),
    vec2(-1.0, -1.0),

    vec2(-1.0, -1.0),
    vec2( 1.0, -1.0),
    vec2( 1.0,  1.0)
);

void main()
{
    vec2 vertexPos = positions[gl_VertexID];
    gl_Position = vec4(vertexPos, 0.0, 1.0);
    fragmentTexCoord = 0.5 * (vertexPos + vec2(1.0, 1.0));
}