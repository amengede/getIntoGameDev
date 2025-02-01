#pragma once
#pragma once
#include "../../config.h"
#include "../vkUtil/shaders.h"
#include "../vkUtil/render_structs.h"

namespace vkInit {

	/**
		Used for returning the pipeline, along with associated data structures,
		after creation.
	*/
	struct ComputePipelineOutBundle {
		vk::PipelineLayout layout;
		vk::Pipeline pipeline;
	};

	class ComputePipelineBuilder {

	public:

		ComputePipelineBuilder(vk::Device device);
		~ComputePipelineBuilder();

		void reset();

		void specify_compute_shader(const char* filename);

		/**
			Make a graphics pipeline, along with renderpass and pipeline layout

			\param specification the struct holding input data, as specified at the top of the file.
			\returns the bundle of data structures created
		*/
		ComputePipelineOutBundle build();

		void add_descriptor_set_layout(vk::DescriptorSetLayout descriptorSetLayout);

		void reset_descriptor_set_layouts();

	private:
		vk::Device device;
		vk::ComputePipelineCreateInfo pipelineInfo = {};

		vk::ShaderModule computeShader = nullptr;
		vk::PipelineShaderStageCreateInfo computeShaderInfo;

		std::vector<vk::DescriptorSetLayout> descriptorSetLayouts;

		void reset_shader_modules();

		/**
			Configure a programmable shader stage.

			\param shaderModule the compiled shader module
			\param stage the shader stage which the module is for
			\returns the shader stage creation info
		*/
		vk::PipelineShaderStageCreateInfo make_shader_info(
			const vk::ShaderModule& shaderModule, const vk::ShaderStageFlagBits& stage);

		/**
			Make a pipeline layout, this consists mostly of describing the
			push constants and descriptor set layouts which will be used.

			\returns the created pipeline layout
		*/
		vk::PipelineLayout make_pipeline_layout();
	};
}