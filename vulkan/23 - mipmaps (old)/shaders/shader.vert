#version 450

layout(location = 0) in vec3 vertexPosition;
layout(location = 1) in vec3 vertexNormal;
layout(location = 2) in vec2 vertexTexCoord;

layout(binding = 0) uniform UniformBufferObject {
	mat4 model;
	mat4 view;
	mat4 proj;
} ubo;

layout(location = 0) out vec3 fragNormal;
layout(location = 1) out vec2 fragTexCoord;

void main() {
	gl_Position = ubo.proj * ubo.view * ubo.model * vec4(vertexPosition, 1.0);
	fragNormal = mat3(ubo.model) * vertexNormal;
	fragTexCoord = vertexTexCoord;
}