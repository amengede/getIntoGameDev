#version 450

layout(location = 0) in vec2 vertexPosition;
layout(location = 1) in vec3 vertexColor;

layout(binding = 0) uniform UniformBufferObject {
	mat4 model;
	mat4 view;
	mat4 proj;
} ubo;

layout(location = 0) out vec3 fragColor;

void main() {
	gl_Position = ubo.proj * ubo.view * ubo.model * vec4(vertexPosition, 0.0, 1.0);
	fragColor = vertexColor;
}