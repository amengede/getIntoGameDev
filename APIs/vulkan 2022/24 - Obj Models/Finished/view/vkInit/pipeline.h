#pragma once
#include "../../config.h"
#include "../vkUtil/shaders.h"
#include "../vkUtil/render_structs.h"
#include "../vkMesh/mesh.h"

namespace vkInit {

	/**
		holds the data structures used to create a pipeline
	*/
	struct GraphicsPipelineInBundle {
		vk::Device device;
		std::string vertexFilepath;
		std::string fragmentFilepath;
		vk::Extent2D swapchainExtent;
		vk::Format swapchainImageFormat, depthFormat;
		std::vector<vk::DescriptorSetLayout> descriptorSetLayouts;
	};

	/**
		Used for returning the pipeline, along with associated data structures,
		after creation.
	*/
	struct GraphicsPipelineOutBundle {
		vk::PipelineLayout layout;
		vk::RenderPass renderpass;
		vk::Pipeline pipeline;
	};

	/**
		Make a graphics pipeline, along with renderpass and pipeline layout

		\param specification the struct holding input data, as specified at the top of the file.
		\returns the bundle of data structures created
	*/
	GraphicsPipelineOutBundle create_graphics_pipeline(GraphicsPipelineInBundle& specification);

	/**
		Configure the vertex input stage.

		\param bindingDescription describes the vertex inputs (ie. layouts)
		\param attributeDescriptions describes the attributes
		\returns the vertex input stage creation info

	*/
	vk::PipelineVertexInputStateCreateInfo make_vertex_input_info(
		const vk::VertexInputBindingDescription& bindingDescription,
		const std::vector<vk::VertexInputAttributeDescription>& attributeDescriptions);

	/**
		\returns the input assembly stage creation info
	*/
	vk::PipelineInputAssemblyStateCreateInfo make_input_assembly_info();

	/**
		Configure a programmable shader stage.

		\param shaderModule the compiled shader module
		\param stage the shader stage which the module is for
		\returns the shader stage creation info
	*/
	vk::PipelineShaderStageCreateInfo make_shader_info(
		const vk::ShaderModule& shaderModule, const vk::ShaderStageFlagBits& stage);

	/**
		Create a viewport.

		\param specification holds relevant data fields
		\returns the created viewport
	*/
	vk::Viewport make_viewport(const GraphicsPipelineInBundle& specification);

	/**
		Create a scissor rectangle.

		\param specification holds relevant data fields
		\returns the created rectangle
	*/
	vk::Rect2D make_scissor(const GraphicsPipelineInBundle& specification);

	/**
		Configure the pipeline's viewport stage.

		\param viewport the viewport specification
		\param scissor the scissor rectangle to apply
		\returns the viewport state creation info
	*/
	vk::PipelineViewportStateCreateInfo make_viewport_state(const vk::Viewport& viewport, const vk::Rect2D& scissor);

	/**
		\returns the creation info for the configured rasterizer stage
	*/
	vk::PipelineRasterizationStateCreateInfo make_rasterizer_info();

	/**
		\returns the creation info for the configured multisampling stage
	*/
	vk::PipelineMultisampleStateCreateInfo make_multisampling_info();

	/**
		\returns the created color blend state
	*/
	vk::PipelineColorBlendAttachmentState make_color_blend_attachment_state();

	/**
		\returns the creation info for the configured color blend stage
	*/
	vk::PipelineColorBlendStateCreateInfo make_color_blend_attachment_stage(
		const vk::PipelineColorBlendAttachmentState& colorBlendAttachment);

	/**
		Make a pipeline layout, this consists mostly of describing the
		push constants and descriptor set layouts which will be used.

		\param device the logical device
		\returns the created pipeline layout
	*/
	vk::PipelineLayout make_pipeline_layout(vk::Device device, std::vector<vk::DescriptorSetLayout> descriptorSetLayouts);

	/**
		Make a renderpass, a renderpass describes the subpasses involved
		as well as the attachments which will be used.

		\param device the logical device
		\param swapchainImageFormat the image format chosen for the swapchain images
		\returns the created renderpass
	*/
	vk::RenderPass make_renderpass(
		vk::Device device, vk::Format swapchainImageFormat, vk::Format depthFormat
	);

	/**
		Make a color attachment description

		\param swapchainImageFormat the image format used by the swapchain
		\returns a description of the corresponding color attachment
	*/
	vk::AttachmentDescription make_color_attachment(const vk::Format& swapchainImageFormat);

	/**
		\returns Make a color attachment refernce
	*/
	vk::AttachmentReference make_color_attachment_reference();

	/**
		Make a depth attachment description

		\param swapchainImageFormat the image format used by the swapchain
		\returns a description of the corresponding depth attachment
	*/
	vk::AttachmentDescription make_depth_attachment(const vk::Format& depthFormat);

	/**
		\returns Make a depth attachment refernce
	*/
	vk::AttachmentReference make_depth_attachment_reference();

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

	GraphicsPipelineOutBundle create_graphics_pipeline(GraphicsPipelineInBundle& specification) {
		/*
		* Build and return a graphics pipeline based on the given info.
		*/

		//The info for the graphics pipeline
		vk::GraphicsPipelineCreateInfo pipelineInfo = {};
		pipelineInfo.flags = vk::PipelineCreateFlags();

		//Shader stages, to be populated later
		std::vector<vk::PipelineShaderStageCreateInfo> shaderStages;

		//Vertex Input
		vk::VertexInputBindingDescription bindingDescription = vkMesh::getPosColorBindingDescription();
		std::vector<vk::VertexInputAttributeDescription> attributeDescriptions = vkMesh::getPosColorAttributeDescriptions();
		vk::PipelineVertexInputStateCreateInfo vertexInputInfo = make_vertex_input_info(bindingDescription, attributeDescriptions);
		pipelineInfo.pVertexInputState = &vertexInputInfo;

		//Input Assembly
		vk::PipelineInputAssemblyStateCreateInfo inputAssemblyInfo = make_input_assembly_info();
		pipelineInfo.pInputAssemblyState = &inputAssemblyInfo;

		//Vertex Shader
		vkLogging::Logger::get_logger()->print("Create vertex shader module");
		vk::ShaderModule vertexShader = vkUtil::createModule(
			specification.vertexFilepath, specification.device
		);
		vk::PipelineShaderStageCreateInfo vertexShaderInfo = make_shader_info(vertexShader, vk::ShaderStageFlagBits::eVertex);
		shaderStages.push_back(vertexShaderInfo);

		//Viewport and Scissor
		vk::Viewport viewport = make_viewport(specification);
		vk::Rect2D scissor = make_scissor(specification);
		vk::PipelineViewportStateCreateInfo viewportState = make_viewport_state(viewport, scissor);
		pipelineInfo.pViewportState = &viewportState;

		//Rasterizer
		vk::PipelineRasterizationStateCreateInfo rasterizer = make_rasterizer_info();
		pipelineInfo.pRasterizationState = &rasterizer;

		//Fragment Shader
		vkLogging::Logger::get_logger()->print("Create fragment shader module");
		vk::ShaderModule fragmentShader = vkUtil::createModule(
			specification.fragmentFilepath, specification.device
		);
		vk::PipelineShaderStageCreateInfo fragmentShaderInfo = make_shader_info(fragmentShader, vk::ShaderStageFlagBits::eFragment);
		shaderStages.push_back(fragmentShaderInfo);
		//Now both shaders have been made, we can declare them to the pipeline info
		pipelineInfo.stageCount = shaderStages.size();
		pipelineInfo.pStages = shaderStages.data();

		//Depth-Stencil
		vk::PipelineDepthStencilStateCreateInfo depthState;
		depthState.flags = vk::PipelineDepthStencilStateCreateFlags();
		depthState.depthTestEnable = true;
		depthState.depthWriteEnable = true;
		depthState.depthCompareOp = vk::CompareOp::eLess;
		depthState.depthBoundsTestEnable = false;
		depthState.stencilTestEnable = false;
		pipelineInfo.pDepthStencilState = &depthState;

		//Multisampling
		vk::PipelineMultisampleStateCreateInfo multisampling = make_multisampling_info();
		pipelineInfo.pMultisampleState = &multisampling;

		//Color Blend
		vk::PipelineColorBlendAttachmentState colorBlendAttachment = make_color_blend_attachment_state();
		vk::PipelineColorBlendStateCreateInfo colorBlending = make_color_blend_attachment_stage(colorBlendAttachment);
		pipelineInfo.pColorBlendState = &colorBlending;

		//Pipeline Layout
		vkLogging::Logger::get_logger()->print("Create Pipeline Layout");
		vk::PipelineLayout pipelineLayout = make_pipeline_layout(specification.device, specification.descriptorSetLayouts);
		pipelineInfo.layout = pipelineLayout;

		//Renderpass
		vkLogging::Logger::get_logger()->print("Create RenderPass");
		vk::RenderPass renderpass = make_renderpass(
			specification.device, specification.swapchainImageFormat, 
			specification.depthFormat
		);
		pipelineInfo.renderPass = renderpass;
		pipelineInfo.subpass = 0;

		//Extra stuff
		pipelineInfo.basePipelineHandle = nullptr;

		//Make the Pipeline
		vkLogging::Logger::get_logger()->print("Create Graphics Pipeline");
		vk::Pipeline graphicsPipeline;
		try {
			graphicsPipeline = (specification.device.createGraphicsPipeline(nullptr, pipelineInfo)).value;
		}
		catch (vk::SystemError err) {
			vkLogging::Logger::get_logger()->print("Failed to create Pipeline");
		}

		GraphicsPipelineOutBundle output;
		output.layout = pipelineLayout;
		output.renderpass = renderpass;
		output.pipeline = graphicsPipeline;

		//Finally clean up by destroying shader modules
		specification.device.destroyShaderModule(vertexShader);
		specification.device.destroyShaderModule(fragmentShader);

		return output;
	}

	vk::PipelineVertexInputStateCreateInfo make_vertex_input_info(
		const vk::VertexInputBindingDescription& bindingDescription,
		const std::vector<vk::VertexInputAttributeDescription>& attributeDescriptions) {

		vk::PipelineVertexInputStateCreateInfo vertexInputInfo = {};
		vertexInputInfo.flags = vk::PipelineVertexInputStateCreateFlags();
		vertexInputInfo.vertexBindingDescriptionCount = 1;
		vertexInputInfo.pVertexBindingDescriptions = &bindingDescription;
		vertexInputInfo.vertexAttributeDescriptionCount = static_cast<uint32_t>(attributeDescriptions.size());
		vertexInputInfo.pVertexAttributeDescriptions = attributeDescriptions.data();
		return vertexInputInfo;
	}

	vk::PipelineInputAssemblyStateCreateInfo make_input_assembly_info() {

		vk::PipelineInputAssemblyStateCreateInfo inputAssemblyInfo = {};
		inputAssemblyInfo.flags = vk::PipelineInputAssemblyStateCreateFlags();
		inputAssemblyInfo.topology = vk::PrimitiveTopology::eTriangleList;

		return inputAssemblyInfo;
	}

	vk::PipelineShaderStageCreateInfo make_shader_info(const vk::ShaderModule& shaderModule, const vk::ShaderStageFlagBits& stage) {

		vk::PipelineShaderStageCreateInfo shaderInfo = {};
		shaderInfo.flags = vk::PipelineShaderStageCreateFlags();
		shaderInfo.stage = stage;
		shaderInfo.module = shaderModule;
		shaderInfo.pName = "main";
		return shaderInfo;
	}

	vk::Viewport make_viewport(const GraphicsPipelineInBundle& specification) {

		vk::Viewport viewport = {};
		viewport.x = 0.0f;
		viewport.y = 0.0f;
		viewport.width = (float)specification.swapchainExtent.width;
		viewport.height = (float)specification.swapchainExtent.height;
		viewport.minDepth = 0.0f;
		viewport.maxDepth = 1.0f;

		return viewport;
	}

	vk::Rect2D make_scissor(const GraphicsPipelineInBundle& specification) {

		vk::Rect2D scissor = {};
		scissor.offset.x = 0.0f;
		scissor.offset.y = 0.0f;
		scissor.extent = specification.swapchainExtent;

		return scissor;
	}

	vk::PipelineViewportStateCreateInfo make_viewport_state(const vk::Viewport& viewport, const vk::Rect2D& scissor) {

		vk::PipelineViewportStateCreateInfo viewportState = {};
		viewportState.flags = vk::PipelineViewportStateCreateFlags();
		viewportState.viewportCount = 1;
		viewportState.pViewports = &viewport;
		viewportState.scissorCount = 1;
		viewportState.pScissors = &scissor;

		return viewportState;
	}

	vk::PipelineRasterizationStateCreateInfo make_rasterizer_info() {

		vk::PipelineRasterizationStateCreateInfo rasterizer = {};
		rasterizer.flags = vk::PipelineRasterizationStateCreateFlags();
		rasterizer.depthClampEnable = VK_FALSE; //discard out of bounds fragments, don't clamp them
		rasterizer.rasterizerDiscardEnable = VK_FALSE; //This flag would disable fragment output
		rasterizer.polygonMode = vk::PolygonMode::eFill;
		rasterizer.lineWidth = 1.0f;
		rasterizer.cullMode = vk::CullModeFlagBits::eBack;
		rasterizer.frontFace = vk::FrontFace::eCounterClockwise;
		rasterizer.depthBiasEnable = VK_FALSE; //Depth bias can be useful in shadow maps.

		return rasterizer;
	}

	vk::PipelineMultisampleStateCreateInfo make_multisampling_info() {

		vk::PipelineMultisampleStateCreateInfo multisampling = {};
		multisampling.flags = vk::PipelineMultisampleStateCreateFlags();
		multisampling.sampleShadingEnable = VK_FALSE;
		multisampling.rasterizationSamples = vk::SampleCountFlagBits::e1;

		return multisampling;
	}

	vk::PipelineColorBlendAttachmentState make_color_blend_attachment_state() {

		vk::PipelineColorBlendAttachmentState colorBlendAttachment = {};
		colorBlendAttachment.colorWriteMask = vk::ColorComponentFlagBits::eR | vk::ColorComponentFlagBits::eG | vk::ColorComponentFlagBits::eB | vk::ColorComponentFlagBits::eA;
		colorBlendAttachment.blendEnable = VK_FALSE;

		return colorBlendAttachment;
	}

	vk::PipelineColorBlendStateCreateInfo make_color_blend_attachment_stage(const vk::PipelineColorBlendAttachmentState& colorBlendAttachment) {

		vk::PipelineColorBlendStateCreateInfo colorBlending = {};
		colorBlending.flags = vk::PipelineColorBlendStateCreateFlags();
		colorBlending.logicOpEnable = VK_FALSE;
		colorBlending.logicOp = vk::LogicOp::eCopy;
		colorBlending.attachmentCount = 1;
		colorBlending.pAttachments = &colorBlendAttachment;
		colorBlending.blendConstants[0] = 0.0f;
		colorBlending.blendConstants[1] = 0.0f;
		colorBlending.blendConstants[2] = 0.0f;
		colorBlending.blendConstants[3] = 0.0f;

		return colorBlending;
	}

	vk::PipelineLayout make_pipeline_layout(vk::Device device, std::vector<vk::DescriptorSetLayout> descriptorSetLayouts) {

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

	vk::RenderPass make_renderpass(
		vk::Device device, vk::Format swapchainImageFormat, vk::Format depthFormat) {

		std::vector<vk::AttachmentDescription> attachments;
		std::vector<vk::AttachmentReference> attachmentReferences;

		//Color Buffer
		attachments.push_back(make_color_attachment(swapchainImageFormat));
		attachmentReferences.push_back(make_color_attachment_reference());

		//Depth Buffer
		attachments.push_back(make_depth_attachment(depthFormat));
		attachmentReferences.push_back(make_depth_attachment_reference());

		//Renderpasses are broken down into subpasses, there's always at least one.
		vk::SubpassDescription subpass = make_subpass(attachmentReferences);

		//Now create the renderpass
		vk::RenderPassCreateInfo renderpassInfo = make_renderpass_info(attachments, subpass);
		try {
			return device.createRenderPass(renderpassInfo);
		}
		catch (vk::SystemError err) {
			vkLogging::Logger::get_logger()->print("Failed to create renderpass!");
		}

	}

	vk::AttachmentDescription make_color_attachment(const vk::Format& swapchainImageFormat) {

		vk::AttachmentDescription colorAttachment = {};
		colorAttachment.flags = vk::AttachmentDescriptionFlags();
		colorAttachment.format = swapchainImageFormat;
		colorAttachment.samples = vk::SampleCountFlagBits::e1;
		colorAttachment.loadOp = vk::AttachmentLoadOp::eClear;
		colorAttachment.storeOp = vk::AttachmentStoreOp::eStore;
		colorAttachment.stencilLoadOp = vk::AttachmentLoadOp::eDontCare;
		colorAttachment.stencilStoreOp = vk::AttachmentStoreOp::eDontCare;
		colorAttachment.initialLayout = vk::ImageLayout::eUndefined;
		colorAttachment.finalLayout = vk::ImageLayout::ePresentSrcKHR;

		return colorAttachment;
	}

	vk::AttachmentReference make_color_attachment_reference() {

		vk::AttachmentReference colorAttachmentRef = {};
		colorAttachmentRef.attachment = 0;
		colorAttachmentRef.layout = vk::ImageLayout::eColorAttachmentOptimal;

		return colorAttachmentRef;
	}

	vk::AttachmentDescription make_depth_attachment(const vk::Format& depthFormat) {

		vk::AttachmentDescription depthAttachment = {};
		depthAttachment.flags = vk::AttachmentDescriptionFlags();
		depthAttachment.format = depthFormat;
		depthAttachment.samples = vk::SampleCountFlagBits::e1;
		depthAttachment.loadOp = vk::AttachmentLoadOp::eClear;
		depthAttachment.storeOp = vk::AttachmentStoreOp::eDontCare;
		depthAttachment.stencilLoadOp = vk::AttachmentLoadOp::eDontCare;
		depthAttachment.stencilStoreOp = vk::AttachmentStoreOp::eDontCare;
		depthAttachment.initialLayout = vk::ImageLayout::eUndefined;
		depthAttachment.finalLayout = vk::ImageLayout::eDepthStencilAttachmentOptimal;

		return depthAttachment;
	}

	vk::AttachmentReference make_depth_attachment_reference() {

		vk::AttachmentReference depthAttachmentRef = {};
		depthAttachmentRef.attachment = 1;
		depthAttachmentRef.layout = vk::ImageLayout::eDepthStencilAttachmentOptimal;

		return depthAttachmentRef;
	}

	vk::SubpassDescription make_subpass(
		const std::vector<vk::AttachmentReference>& attachments) {

		vk::SubpassDescription subpass = {};
		subpass.flags = vk::SubpassDescriptionFlags();
		subpass.pipelineBindPoint = vk::PipelineBindPoint::eGraphics;
		subpass.colorAttachmentCount = 1;
		subpass.pColorAttachments = &attachments[0];
		subpass.pDepthStencilAttachment = &attachments[1];

		return subpass;
	}

	vk::RenderPassCreateInfo make_renderpass_info(
		const std::vector<vk::AttachmentDescription>& attachments, 
		const vk::SubpassDescription& subpass) {

		vk::RenderPassCreateInfo renderpassInfo = {};
		renderpassInfo.flags = vk::RenderPassCreateFlags();
		renderpassInfo.attachmentCount = attachments.size();
		renderpassInfo.pAttachments = attachments.data();
		renderpassInfo.subpassCount = 1;
		renderpassInfo.pSubpasses = &subpass;

		return renderpassInfo;
	}
}