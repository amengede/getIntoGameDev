#version 450
#extension GL_ARB_separate_shader_objects : enable

layout(location = 0) in vec3 fragNormal;
layout(location = 1) in vec2 fragTexCoord;

layout(binding = 1) uniform sampler2D texSampler;

layout(location = 0) out vec4 outColor;

void main() {
	//lighting
	vec3 sunDirection = normalize(vec3(1.0, 0.0, 1.0));
	float lightAmount = max(0.0, dot(fragNormal, sunDirection));
	vec4 result = vec4(lightAmount * vec3(1.0), 1.0) * texture(texSampler, fragTexCoord);

	float gamma = 2.2;
	result.rgb = pow(result.rgb, vec3(1.0/gamma));
	outColor = result;
}