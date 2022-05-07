#version 450

layout(location = 0) in vec3 vertexPosition;
layout(location = 1) in vec3 vertexNormal;
layout(location = 2) in vec2 vertexTexCoord;

layout(binding = 0) uniform UniformBufferObject {
	mat4 view;
	mat4 projection;
} ubo;

layout(push_constant) uniform constants {
	mat4 model;
} PushConstants;

layout(location = 0) out vec3 fragNormal;
layout(location = 1) out vec2 fragTexCoord;

void main() {
	gl_Position = ubo.projection * ubo.view * PushConstants.model * vec4(vertexPosition, 1.0);
	fragNormal = mat3(PushConstants.model) * vertexNormal;
	fragTexCoord = vertexTexCoord;
}