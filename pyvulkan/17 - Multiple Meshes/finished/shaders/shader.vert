#version 450

layout(location = 0) in vec2 vertexPosition;
layout(location = 1) in vec3 vertexColor;

layout(location = 0) out vec3 fragColor;

layout (push_constant) uniform constants {
	mat4 model;
} ObjectData;

void main() {
	gl_Position = ObjectData.model * vec4(vertexPosition, 0.0, 1.0);
	fragColor = vertexColor;
}
