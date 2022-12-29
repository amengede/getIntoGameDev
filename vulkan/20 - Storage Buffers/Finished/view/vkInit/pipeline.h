#pragma once
#include "../../config.h"
#include "../vkUtil/shaders.h"
#include "../vkUtil/render_structs.h"
#include "../vkMesh/mesh.h"

namespace vkInit {

	/**
	* Holds input fields for pipeline creation
	* 
	* @param device					the logical device
	* @param vertexFilepath			location of the vertex shader spir-v file
	* @param fragmentFilepath		location of the fragment shader spir-v file
	* @param swapchainExtent		size of the swapchain images
	* @param swapchainImageFormat	the pixel format of the swapchain iamges
	*/
	struct GraphicsPipelineInBundle {
		vk::Device device;
		std::string vertexFilepath;
		std::string fragmentFilepath;
		vk::Extent2D swapchainExtent;
		vk::Format swapchainImageFormat;
		vk::DescriptorSetLayout descriptorSetLayout;
	};

	/**
	* Holds the various outputs resulting from pipeline creation
	* 
	* @param layout		the graphics pipeline
	* @param renderpass the renderpass for the pipeline
	* @param pipeline	the graphics pipeline
	*/
	struct GraphicsPipelineOutBundle {
		vk::PipelineLayout layout;
		vk::RenderPass renderpass;
		vk::Pipeline pipeline;
	};

	/**
	* Create a graphics pipeline
	*
	* @param specification	holds the various required input fields
	* @param debug			whether to print extra information
	* @return				the various created objects
	*/
	GraphicsPipelineOutBundle create_graphics_pipeline(GraphicsPipelineInBundle& specification);

	/**
		Configure the vertex input stage
	*/
	vk::PipelineVertexInputStateCreateInfo make_vertex_input_info(
		const vk::VertexInputBindingDescription& bindingDescription,
		const std::array<vk::VertexInputAttributeDescription, 2>& attributeDescriptions);

	/**
		Configure the input assembly stage
	*/
	vk::PipelineInputAssemblyStateCreateInfo make_input_assembly_info();

	vk::PipelineShaderStageCreateInfo make_shader_info(
		const vk::ShaderModule& shaderModule, const vk::ShaderStageFlagBits& stage);

	vk::Viewport make_viewport(const GraphicsPipelineInBundle& specification);

	vk::Rect2D make_scissor(const GraphicsPipelineInBundle& specification);

	vk::PipelineViewportStateCreateInfo make_viewport_state(const vk::Viewport& viewport, const vk::Rect2D& scissor);

	vk::PipelineRasterizationStateCreateInfo make_rasterizer_info();

	vk::PipelineMultisampleStateCreateInfo make_multisampling_info();

	vk::PipelineColorBlendAttachmentState make_color_blend_attachment_state();

	vk::PipelineColorBlendStateCreateInfo make_color_blend_attachment_stage(
		const vk::PipelineColorBlendAttachmentState& colorBlendAttachment);

	/**
	* Make the layout for the graphics pipeline
	*
	* @param device					the logical device
	* @param descriptorSetLayout	the descriptor set layout
	* @returns		the pipeline layout
	*/
	vk::PipelineLayout make_pipeline_layout(vk::Device device, vk::DescriptorSetLayout descriptorSetLayout);

	vk::PushConstantRange make_push_constant_info();

	/**
	* Make the renderpass for the swapchain
	*
	* @param						device the logical device
	* @param swapchainImageFormat	the pixel format of the swapchain images
	* @param debug					whether to print extra information
	* @return						the created renderpass
	*/
	vk::RenderPass make_renderpass(vk::Device device, vk::Format swapchainImageFormat);

	vk::AttachmentDescription make_color_attachment(const vk::Format& swapchainImageFormat);

	vk::AttachmentReference make_color_attachment_reference();

	vk::SubpassDescription make_subpass(const vk::AttachmentReference& colorAttachmentRef);

	vk::RenderPassCreateInfo make_renderpass_info(
		const vk::AttachmentDescription& colorAttachment, const vk::SubpassDescription& subpass);

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
		std::array<vk::VertexInputAttributeDescription, 2> attributeDescriptions = vkMesh::getPosColorAttributeDescriptions();
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

		//Multisampling
		vk::PipelineMultisampleStateCreateInfo multisampling = make_multisampling_info();
		pipelineInfo.pMultisampleState = &multisampling;

		//Color Blend
		vk::PipelineColorBlendAttachmentState colorBlendAttachment = make_color_blend_attachment_state();
		vk::PipelineColorBlendStateCreateInfo colorBlending = make_color_blend_attachment_stage(colorBlendAttachment);
		pipelineInfo.pColorBlendState = &colorBlending;

		//Pipeline Layout
		vkLogging::Logger::get_logger()->print("Create Pipeline Layout");
		vk::PipelineLayout pipelineLayout = make_pipeline_layout(specification.device, specification.descriptorSetLayout);
		pipelineInfo.layout = pipelineLayout;

		//Renderpass
		vkLogging::Logger::get_logger()->print("Create RenderPass");
		vk::RenderPass renderpass = make_renderpass(
			specification.device, specification.swapchainImageFormat
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
		const std::array<vk::VertexInputAttributeDescription, 2>& attributeDescriptions) {

		vk::PipelineVertexInputStateCreateInfo vertexInputInfo = {};
		vertexInputInfo.flags = vk::PipelineVertexInputStateCreateFlags();
		vertexInputInfo.vertexBindingDescriptionCount = 1;
		vertexInputInfo.pVertexBindingDescriptions = &bindingDescription;
		vertexInputInfo.vertexAttributeDescriptionCount = 2;
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
		rasterizer.frontFace = vk::FrontFace::eClockwise;
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

	vk::PipelineLayout make_pipeline_layout(vk::Device device, vk::DescriptorSetLayout descriptorSetLayout) {

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

		layoutInfo.setLayoutCount = 1;
		layoutInfo.pSetLayouts = &descriptorSetLayout;

		layoutInfo.pushConstantRangeCount = 0;

		try {
			return device.createPipelineLayout(layoutInfo);
		}
		catch (vk::SystemError err) {
			vkLogging::Logger::get_logger()->print("Failed to create pipeline layout!");
		}
	}

	vk::RenderPass make_renderpass(vk::Device device, vk::Format swapchainImageFormat) {

		//Define a general attachment, with its load/store operations
		vk::AttachmentDescription colorAttachment = make_color_attachment(swapchainImageFormat);

		//Declare that attachment to be color buffer 0 of the framebuffer
		vk::AttachmentReference colorAttachmentRef = make_color_attachment_reference();

		//Renderpasses are broken down into subpasses, there's always at least one.
		vk::SubpassDescription subpass = make_subpass(colorAttachmentRef);

		//Now create the renderpass
		vk::RenderPassCreateInfo renderpassInfo = make_renderpass_info(colorAttachment, subpass);
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

	vk::SubpassDescription make_subpass(const vk::AttachmentReference& colorAttachmentRef) {

		vk::SubpassDescription subpass = {};
		subpass.flags = vk::SubpassDescriptionFlags();
		subpass.pipelineBindPoint = vk::PipelineBindPoint::eGraphics;
		subpass.colorAttachmentCount = 1;
		subpass.pColorAttachments = &colorAttachmentRef;

		return subpass;
	}

	vk::RenderPassCreateInfo make_renderpass_info(const vk::AttachmentDescription& colorAttachment, const vk::SubpassDescription& subpass) {

		vk::RenderPassCreateInfo renderpassInfo = {};
		renderpassInfo.flags = vk::RenderPassCreateFlags();
		renderpassInfo.attachmentCount = 1;
		renderpassInfo.pAttachments = &colorAttachment;
		renderpassInfo.subpassCount = 1;
		renderpassInfo.pSubpasses = &subpass;

		return renderpassInfo;
	}
}