#pragma once
#include "../../config.h"
#include "../vkUtil/shaders.h"
#include "../vkUtil/render_structs.h"

namespace vkInit {

	/**
		Used for returning the pipeline, along with associated data structures,
		after creation.
	*/
	struct GraphicsPipelineOutBundle {
		vk::PipelineLayout layout;
		vk::RenderPass renderpass;
		vk::Pipeline pipeline;
	};

	class PipelineBuilder {

	public:

		PipelineBuilder(vk::Device device);
		~PipelineBuilder();

		void reset();

		/**
			Configure the vertex input stage.

			\param bindingDescription describes the vertex inputs (ie. layouts)
			\param attributeDescriptions describes the attributes
			\returns the vertex input stage creation info

		*/
		void specify_vertex_format(
			vk::VertexInputBindingDescription bindingDescription, 
			std::vector<vk::VertexInputAttributeDescription> attributeDescriptions);

		void specify_vertex_shader(const char* filename);

		void specify_fragment_shader(const char* filename);

		void specify_swapchain_extent(vk::Extent2D screen_size);

		void specify_depth_attachment(const vk::Format& depthFormat, uint32_t attachment_index);

		void clear_depth_attachment();

		void add_color_attachment(const vk::Format& format, uint32_t attachment_index);

		/**
			Make a graphics pipeline, along with renderpass and pipeline layout

			\param specification the struct holding input data, as specified at the top of the file.
			\returns the bundle of data structures created
		*/
		GraphicsPipelineOutBundle build();

		void add_descriptor_set_layout(vk::DescriptorSetLayout descriptorSetLayout);

		void reset_descriptor_set_layouts();

		private:
			vk::Device device;
			vk::GraphicsPipelineCreateInfo pipelineInfo = {};
			
			vk::VertexInputBindingDescription bindingDescription;
			std::vector<vk::VertexInputAttributeDescription> attributeDescriptions;
			vk::PipelineVertexInputStateCreateInfo vertexInputInfo = {};
			vk::PipelineInputAssemblyStateCreateInfo inputAssemblyInfo = {};

			std::vector<vk::PipelineShaderStageCreateInfo> shaderStages;
			vk::ShaderModule vertexShader = nullptr, fragmentShader = nullptr;
			vk::PipelineShaderStageCreateInfo vertexShaderInfo, fragmentShaderInfo;

			vk::Extent2D swapchainExtent;
			vk::Viewport viewport = {};
			vk::Rect2D scissor = {};
			vk::PipelineViewportStateCreateInfo viewportState = {};

			vk::PipelineRasterizationStateCreateInfo rasterizer = {};

			vk::PipelineDepthStencilStateCreateInfo depthState;
			std::unordered_map<uint32_t, vk::AttachmentDescription> attachmentDescriptions;
			std::unordered_map<uint32_t, vk::AttachmentReference> attachmentReferences;
			std::vector<vk::AttachmentDescription> flattenedAttachmentDescriptions;
			std::vector<vk::AttachmentReference> flattenedAttachmentReferences;

			vk::PipelineMultisampleStateCreateInfo multisampling = {};

			vk::PipelineColorBlendAttachmentState colorBlendAttachment = {};
			vk::PipelineColorBlendStateCreateInfo colorBlending = {};

			std::vector<vk::DescriptorSetLayout> descriptorSetLayouts;

			void reset_vertex_format();

			void reset_shader_modules();

			void reset_renderpass_attachments();

			/**
				Make an attachment description

				\param format the image format for the underlying resource
				\param finalLayout the expected final layout after implicit transition (acquisition)
				\returns a description of the corresponding attachment
			*/
			vk::AttachmentDescription make_renderpass_attachment(
				const vk::Format& format, vk::AttachmentLoadOp loadOp,
				vk::AttachmentStoreOp storeOp, vk::ImageLayout initialLayout, vk::ImageLayout finalLayout);

			/**
				\returns Make a renderpass attachment reference
			*/
			vk::AttachmentReference make_attachment_reference(
				uint32_t attachment_index, vk::ImageLayout layout);

			/**
				set up the input assembly stage
			*/
			void configure_input_assembly();

			/**
				Configure a programmable shader stage.

				\param shaderModule the compiled shader module
				\param stage the shader stage which the module is for
				\returns the shader stage creation info
			*/
			vk::PipelineShaderStageCreateInfo make_shader_info(
				const vk::ShaderModule& shaderModule, const vk::ShaderStageFlagBits& stage);
			
			/**
				Configure the pipeline's viewport stage.

				\param viewport the viewport specification
				\param scissor the scissor rectangle to apply
				\returns the viewport state creation info
			*/
			vk::PipelineViewportStateCreateInfo make_viewport_state();

			/**
				sets the creation info for the configured rasterizer stage
			*/
			void make_rasterizer_info();

			/**
				configures the multisampling stage
			*/
			void configure_multisampling();

			/**
				configures the color blending stage
			*/
			void configure_color_blending();
			
			/**
				Make a pipeline layout, this consists mostly of describing the
				push constants and descriptor set layouts which will be used.

				\returns the created pipeline layout
			*/
			vk::PipelineLayout make_pipeline_layout();

			/**
				Make a renderpass, a renderpass describes the subpasses involved
				as well as the attachments which will be used.

				\returns the created renderpass
			*/
			vk::RenderPass make_renderpass();

			/**
				Make a simple subpass.

				\param colorAttachmentRef a reference to a color attachment for the color buffer
				\returns a description of the subpass
			*/
			vk::SubpassDescription make_subpass(
				const std::vector<vk::AttachmentReference>& attachments
			);

			/**
				Make a simple renderpass.

				\param colorAttachment the color attachment for the color buffer
				\param subpass a description of the subpass
				\returns creation info for the renderpass
			*/
			vk::RenderPassCreateInfo make_renderpass_info(
				const std::vector<vk::AttachmentDescription>& attachments,
				const vk::SubpassDescription& subpass
			);
	};
}