from config import *
import shaders
import vklogging
import mesh

class InputBundle:


    def __init__(self, device, 
    swapchainImageFormat, swapchainExtent, 
    vertexFilepath, fragmentFilepath,
    descriptorSetLayouts):

        self.device = device
        self.swapchainImageFormat = swapchainImageFormat
        self.swapchainExtent = swapchainExtent
        self.vertexFilepath = vertexFilepath
        self.fragmentFilepath = fragmentFilepath
        self.descriptorSetLayouts = descriptorSetLayouts

class OuputBundle:


    def __init__(self, pipelineLayout, renderPass, pipeline):

        self.pipelineLayout = pipelineLayout
        self.renderPass = renderPass
        self.pipeline = pipeline

def create_render_pass(device, swapchainImageFormat):
    
    colorAttachment = VkAttachmentDescription(
        format = swapchainImageFormat,
        samples = VK_SAMPLE_COUNT_1_BIT,

        loadOp = VK_ATTACHMENT_LOAD_OP_CLEAR,
        storeOp = VK_ATTACHMENT_STORE_OP_STORE,

        stencilLoadOp = VK_ATTACHMENT_LOAD_OP_DONT_CARE,
        stencilStoreOp = VK_ATTACHMENT_STORE_OP_DONT_CARE,

        initialLayout=VK_IMAGE_LAYOUT_UNDEFINED,
        finalLayout=VK_IMAGE_LAYOUT_PRESENT_SRC_KHR 
    )

    colorAttachmentRef = VkAttachmentReference(
        attachment=0,
        layout=VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL
    )

    subpass = VkSubpassDescription(
        pipelineBindPoint=VK_PIPELINE_BIND_POINT_GRAPHICS,
        colorAttachmentCount=1,
        pColorAttachments=colorAttachmentRef
    )

    renderPassInfo = VkRenderPassCreateInfo(
        sType=VK_STRUCTURE_TYPE_RENDER_PASS_CREATE_INFO,
        attachmentCount=1,
        pAttachments=colorAttachment,
        subpassCount=1,
        pSubpasses=subpass
    )

    return vkCreateRenderPass(device, renderPassInfo, None)

def create_pipeline_layout(device, descriptorSetLayouts):

    """
    typedef struct VkPipelineLayoutCreateInfo {
		VkStructureType                 sType;
		const void*                     pNext;
		VkPipelineLayoutCreateFlags     flags;
		uint32_t                        setLayoutCount;
		const VkDescriptorSetLayout*    pSetLayouts;
		uint32_t                        pushConstantRangeCount;
		const VkPushConstantRange*      pPushConstantRanges;
	} VkPipelineLayoutCreateInfo;
    """

    pipelineLayoutInfo = VkPipelineLayoutCreateInfo(
        pushConstantRangeCount = 0, pPushConstantRanges = None,
        setLayoutCount = len(descriptorSetLayouts), 
        pSetLayouts = descriptorSetLayouts
    )

    return vkCreatePipelineLayout(
        device = device, pCreateInfo = pipelineLayoutInfo, pAllocator = None
    )

def create_graphics_pipeline(inputBundle: InputBundle):

    #vertex input stage
    #At this stage, no vertex data is being fetched.
    bindingDescription = mesh.get_pos_color_binding_description()
    attributeDescriptions = mesh.get_pos_color_attribute_descriptions()
    vertexInputInfo = VkPipelineVertexInputStateCreateInfo(
        sType=VK_STRUCTURE_TYPE_PIPELINE_VERTEX_INPUT_STATE_CREATE_INFO,
        vertexBindingDescriptionCount = 1, 
        pVertexBindingDescriptions = (bindingDescription,),
        vertexAttributeDescriptionCount = len(attributeDescriptions), 
        pVertexAttributeDescriptions= attributeDescriptions
    )

    #vertex shader transforms vertices appropriately
    vklogging.logger.print(f"Load shader module: {inputBundle.vertexFilepath}")
    vertexShaderModule = shaders.create_shader_module(inputBundle.device, inputBundle.vertexFilepath)
    vertexShaderStageInfo = VkPipelineShaderStageCreateInfo(
        sType=VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO,
        stage=VK_SHADER_STAGE_VERTEX_BIT,
        module=vertexShaderModule,
        pName="main"
    )

    #input assembly, which construction method to use with vertices
    inputAssembly = VkPipelineInputAssemblyStateCreateInfo(
        sType=VK_STRUCTURE_TYPE_PIPELINE_INPUT_ASSEMBLY_STATE_CREATE_INFO,
        topology=VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST,
        primitiveRestartEnable=VK_FALSE #allows "breaking up" of strip topologies
    )

    #transformation from image to framebuffer: stretch
    viewport = VkViewport(
        x=0,
        y=0,
        width=inputBundle.swapchainExtent.width,
        height = inputBundle.swapchainExtent.height,
        minDepth=0.0,
        maxDepth=1.0
    )

    #transformation from image to framebuffer: cutout
    scissor = VkRect2D(
        offset=[0,0],
        extent=inputBundle.swapchainExtent
    )

    #these two transformations combine to define the state of the viewport
    viewportState = VkPipelineViewportStateCreateInfo(
        sType=VK_STRUCTURE_TYPE_PIPELINE_VIEWPORT_STATE_CREATE_INFO,
        viewportCount=1,
        pViewports=viewport,
        scissorCount=1,
        pScissors=scissor
    )

    #rasterizer interpolates between vertices to produce fragments, it
    #also performs visibility tests
    raterizer = VkPipelineRasterizationStateCreateInfo(
        sType=VK_STRUCTURE_TYPE_PIPELINE_RASTERIZATION_STATE_CREATE_INFO,
        depthClampEnable=VK_FALSE,
        rasterizerDiscardEnable=VK_FALSE,
        polygonMode=VK_POLYGON_MODE_FILL,
        lineWidth=1.0,
        cullMode=VK_CULL_MODE_BACK_BIT,
        frontFace=VK_FRONT_FACE_CLOCKWISE,
        depthBiasEnable=VK_FALSE #optional transform on depth values
    )

    #multisampling parameters
    multisampling = VkPipelineMultisampleStateCreateInfo(
        sType=VK_STRUCTURE_TYPE_PIPELINE_MULTISAMPLE_STATE_CREATE_INFO,
        sampleShadingEnable=VK_FALSE,
        rasterizationSamples=VK_SAMPLE_COUNT_1_BIT
    )

    #fragment shader takes fragments from the rasterizer and colours them
    #appropriately
    vklogging.logger.print(f"Load shader module: {inputBundle.fragmentFilepath}")
    fragmentShaderModule = shaders.create_shader_module(inputBundle.device, inputBundle.fragmentFilepath)
    fragmentShaderStageInfo = VkPipelineShaderStageCreateInfo(
        sType=VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO,
        stage=VK_SHADER_STAGE_FRAGMENT_BIT,
        module=fragmentShaderModule,
        pName="main"
    )

    shaderStages = [vertexShaderStageInfo, fragmentShaderStageInfo]

    #color blending, take the output from the fragment shader then incorporate it with the
    #existing pixel, if it has been set.
    colorBlendAttachment = VkPipelineColorBlendAttachmentState(
        colorWriteMask=VK_COLOR_COMPONENT_R_BIT | VK_COLOR_COMPONENT_G_BIT | VK_COLOR_COMPONENT_B_BIT | VK_COLOR_COMPONENT_A_BIT,
        blendEnable=VK_FALSE #blend function
    )
    colorBlending = VkPipelineColorBlendStateCreateInfo(
        sType=VK_STRUCTURE_TYPE_PIPELINE_COLOR_BLEND_STATE_CREATE_INFO,
        logicOpEnable=VK_FALSE, #logical operations
        attachmentCount=1,
        pAttachments=colorBlendAttachment,
        blendConstants=[0.0, 0.0, 0.0, 0.0]
    )

    pipelineLayout = create_pipeline_layout(
        inputBundle.device, inputBundle.descriptorSetLayouts)
    renderPass = create_render_pass(inputBundle.device, inputBundle.swapchainImageFormat)

    pipelineInfo = VkGraphicsPipelineCreateInfo(
        sType=VK_STRUCTURE_TYPE_GRAPHICS_PIPELINE_CREATE_INFO,
        stageCount=2,
        pStages=shaderStages,
        pVertexInputState=vertexInputInfo,
        pInputAssemblyState=inputAssembly,
        pViewportState=viewportState,
        pRasterizationState=raterizer,
        pMultisampleState=multisampling,
        pDepthStencilState=None,
        pColorBlendState=colorBlending,
        layout=pipelineLayout,
        renderPass=renderPass,
        subpass=0 #index to subpass 0, the only subpass
    )

    #vkCreateGraphicsPipelines(device, pipelineCache, createInfoCount, pCreateInfos, pAllocator, pPipelines=None)
    graphicsPipeline = vkCreateGraphicsPipelines(inputBundle.device, VK_NULL_HANDLE, 1, pipelineInfo, None)[0]

    vkDestroyShaderModule(inputBundle.device, vertexShaderModule, None)
    vkDestroyShaderModule(inputBundle.device, fragmentShaderModule, None)

    return OuputBundle(
        pipelineLayout = pipelineLayout,
        renderPass = renderPass,
        pipeline = graphicsPipeline
    )