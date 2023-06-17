#include "compute_pipeline.h"
#include "../../control/logging.h"

vkInit::ComputePipelineBuilder::ComputePipelineBuilder(vk::Device device) {
	this->device = device;
	reset();

	//Some stages are fixed with sensible defaults and don't
	//need to be reconfigured
	pipelineInfo.basePipelineHandle = nullptr;
}

vkInit::ComputePipelineBuilder::~ComputePipelineBuilder() {
	reset();
}

void vkInit::ComputePipelineBuilder::reset() {

	pipelineInfo.flags = vk::PipelineCreateFlags();

	reset_shader_modules();
	reset_descriptor_set_layouts();
}

void vkInit::ComputePipelineBuilder::reset_shader_modules() {
	if (computeShader) {
		device.destroyShaderModule(computeShader);
		computeShader = nullptr;
	}
}

void vkInit::ComputePipelineBuilder::specify_compute_shader(const char* filename) {

	if (computeShader) {
		device.destroyShaderModule(computeShader);
		computeShader = nullptr;
	}

	vkLogging::Logger::get_logger()->print("Create compute shader module");
	computeShader = vkUtil::createModule(filename, device);
	computeShaderInfo = make_shader_info(computeShader, vk::ShaderStageFlagBits::eCompute);
}

vk::PipelineShaderStageCreateInfo vkInit::ComputePipelineBuilder::make_shader_info(
	const vk::ShaderModule& shaderModule, const vk::ShaderStageFlagBits& stage) {

	vk::PipelineShaderStageCreateInfo shaderInfo = {};
	shaderInfo.flags = vk::PipelineShaderStageCreateFlags();
	shaderInfo.stage = stage;
	shaderInfo.module = shaderModule;
	shaderInfo.pName = "main";
	return shaderInfo;
}

void vkInit::ComputePipelineBuilder::add_descriptor_set_layout(vk::DescriptorSetLayout descriptorSetLayout) {
	descriptorSetLayouts.push_back(descriptorSetLayout);
}

void vkInit::ComputePipelineBuilder::reset_descriptor_set_layouts() {
	descriptorSetLayouts.clear();
}

vkInit::ComputePipelineOutBundle vkInit::ComputePipelineBuilder::build() {

	//Compute Shader
	pipelineInfo.stage = computeShaderInfo;

	//Pipeline Layout
	vkLogging::Logger::get_logger()->print("Create Pipeline Layout");
	vk::PipelineLayout pipelineLayout = make_pipeline_layout();
	pipelineInfo.layout = pipelineLayout;

	//Make the Pipeline
	vkLogging::Logger::get_logger()->print("Create Compute Pipeline");
	vk::Pipeline computePipeline;
	try {
		computePipeline = (device.createComputePipeline(nullptr, pipelineInfo)).value;
	}
	catch (vk::SystemError err) {
		vkLogging::Logger::get_logger()->print("Failed to create Pipeline");
	}

	ComputePipelineOutBundle output;
	output.layout = pipelineLayout;
	output.pipeline = computePipeline;

	return output;
}

vk::PipelineLayout vkInit::ComputePipelineBuilder::make_pipeline_layout() {

	/*
	typedef struct VkPipelineLayoutCreateInfo {
		VkStructureType                 sType;
		const void*                     pNext;
		VkPipelineLayoutCreateFlags     flags;
		uint32_t                        setLayoutCount;
		const VkDescriptorSetLayout*    pSetLayouts;
		uint32_t                        pushConstantRangeCount;
		const VkPushConstantRange*      pPushConstantRanges;
	} VkPipelineLayoutCreateInfo;
	*/

	vk::PipelineLayoutCreateInfo layoutInfo;
	layoutInfo.flags = vk::PipelineLayoutCreateFlags();

	layoutInfo.setLayoutCount = static_cast<uint32_t>(descriptorSetLayouts.size());
	layoutInfo.pSetLayouts = descriptorSetLayouts.data();

	layoutInfo.pushConstantRangeCount = 0;

	try {
		return device.createPipelineLayout(layoutInfo);
	}
	catch (vk::SystemError err) {
		vkLogging::Logger::get_logger()->print("Failed to create pipeline layout!");
	}
}