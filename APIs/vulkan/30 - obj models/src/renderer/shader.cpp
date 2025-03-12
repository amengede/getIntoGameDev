#include "shader.h"
#include "../logging/logger.h"
#include "../backend/file.h"
#include <sstream>
#include <fstream>

PipelineLayoutBuilder::PipelineLayoutBuilder(Device& device):
    device(device) {}

vk::PipelineLayout PipelineLayoutBuilder::build() {

    vk::PipelineLayoutCreateInfo layoutInfo;
    layoutInfo.flags = vk::PipelineLayoutCreateFlags();

    layoutInfo.setLayoutCount = descriptorSetLayouts.size;
    layoutInfo.pSetLayouts = descriptorSetLayouts.data;

    layoutInfo.pushConstantRangeCount = 0;

    Logger* logger = Logger::get_logger();
    auto result = device.device.createPipelineLayout(layoutInfo);

    if (result.result != vk::Result::eSuccess) {
        logger->print("Failed to create pipeline layout");
        return nullptr;
    }

    logger->print("Successfully created pipeline layout");
    VkPipelineLayout handle = result.value;
    device.deletionQueue.push_back([handle, logger](vk::Device device) {
        device.destroyPipelineLayout(handle);
        logger->print("Destroyed Pipeline Layout");
    });
    reset();
    return result.value;
}

void PipelineLayoutBuilder::add(vk::DescriptorSetLayout descriptorSetLayout) {
    descriptorSetLayouts.push_back(descriptorSetLayout);
}

void PipelineLayoutBuilder::reset() {
    descriptorSetLayouts.clear();
}

DynamicArray<vk::ShaderEXT> make_shader_objects(vk::Device logicalDevice, 
    const char* name, vk::detail::DispatchLoaderDynamic& dl,
    std::deque<std::function<void(vk::Device)>>& deviceDeletionQueue) {

    Logger* logger = Logger::get_logger();

    std::stringstream filenameBuilder;
    std::string filename;

    /*
    ShaderCreateInfoEXT(
        vk::ShaderCreateFlagsEXT flags_ = {},
        vk::ShaderStageFlagBits  stage_ = vk::ShaderStageFlagBits::eVertex,
        vk::ShaderStageFlags nextStage_ = {},
        vk::ShaderCodeTypeEXT codeType_ = vk::ShaderCodeTypeEXT::eBinary,
        size_t               codeSize_  = {},
        const void *         pCode_     = {},
        const char *         pName_     = {},
        uint32_t    setLayoutCount_     = {},
        const vk::DescriptorSetLayout * pSetLayouts_ = {},
        uint32_t pushConstantRangeCount_ = {},
        const vk::PushConstantRange * pPushConstantRanges_ = {},
        const kv::SpecializationInfo * pSpecializationInfo_ = {},
        const void * pNext_            = nullptr)
    */

    vk::ShaderCreateFlagsEXT flags = vk::ShaderCreateFlagBitsEXT::eLinkStage;
    vk::ShaderStageFlags nextStage = vk::ShaderStageFlagBits::eFragment;

    filenameBuilder << "shaders/" << name << ".vert";
    filename = filenameBuilder.str();
    filenameBuilder.str("");
    DynamicArray<char> vertexCode = read_file(filename.c_str());

    vk::ShaderCodeTypeEXT codeType = vk::ShaderCodeTypeEXT::eSpirv;
    const char* pName = "main";

    vk::ShaderCreateInfoEXT vertexInfo = {};
    vertexInfo.setFlags(flags);
    vertexInfo.setStage(vk::ShaderStageFlagBits::eVertex);
    vertexInfo.setNextStage(nextStage);
    vertexInfo.setCodeType(codeType);
    vertexInfo.setCodeSize(vertexCode.size);
    vertexInfo.setPCode(vertexCode.data);
    vertexInfo.setPName(pName);

    filenameBuilder << "shaders/" << name << ".frag";
    filename = filenameBuilder.str();
    filenameBuilder.str("");
    DynamicArray<char> fragmentCode = read_file(filename.c_str());

    vk::ShaderCreateInfoEXT fragmentInfo = {};
    fragmentInfo.setFlags(flags);
    fragmentInfo.setStage(vk::ShaderStageFlagBits::eFragment);
    fragmentInfo.setCodeType(codeType);
    fragmentInfo.setCodeSize(fragmentCode.size);
    fragmentInfo.setPCode(fragmentCode.data);
    fragmentInfo.setPName(pName);

    /*
        VKAPI_ATTR VkResult VKAPI_CALL vkCreateShadersEXT(
            VkDevice                     device,
            uint32_t                     createInfoCount,
            const VkShaderCreateInfoEXT* pCreateInfos,
            const VkAllocationCallbacks* pAllocator,
            VkShaderEXT*                 pShaders);
    */
    DynamicArray<vk::ShaderCreateInfoEXT> shaderInfo;
    shaderInfo.push_back(vertexInfo);
    shaderInfo.push_back(fragmentInfo);
    DynamicArray<vk::ShaderEXT> shaders;
    shaders.resize(2);

    auto result = logicalDevice.createShadersEXT(2, shaderInfo.data, nullptr, shaders.data, dl);
    
    
    if (result == vk::Result::eSuccess) {
        logger->print("Successfully made shaders");
        VkShaderEXT vertexShader = shaders[0];
        deviceDeletionQueue.push_back([vertexShader, dl](vk::Device device) {
            device.destroyShaderEXT(vertexShader, nullptr, dl);
        });
        VkShaderEXT fragmentShader = shaders[1];
        deviceDeletionQueue.push_back([fragmentShader, dl](vk::Device device) {
            device.destroyShaderEXT(fragmentShader, nullptr, dl);
        });
    }
    else {
        logger->print("Shader creation failed");
    }
    return shaders;
}

vk::ShaderEXT make_compute_shader(Device device,
    const char* name,
    vk::detail::DispatchLoaderDynamic& dl,
    DynamicArray<vk::DescriptorSetLayout>& setLayouts) {

    Logger* logger = Logger::get_logger();

    std::stringstream filenameBuilder;
    std::string filename;

    filenameBuilder << "shaders/" << name << ".spv";
    filename = filenameBuilder.str();
    filenameBuilder.str("");
    
    DynamicArray<char> srcCode = read_file(filename.c_str());

    vk::ShaderCodeTypeEXT codeType = vk::ShaderCodeTypeEXT::eSpirv;
    const char* pName = "main";

    vk::ShaderCreateInfoEXT shaderInfo = {};
    shaderInfo.setStage(vk::ShaderStageFlagBits::eCompute);
    shaderInfo.setCodeType(codeType);
    shaderInfo.setCodeSize(srcCode.size);
    shaderInfo.setPCode(srcCode.data);
    shaderInfo.setPName(pName);
    shaderInfo.setSetLayoutCount(setLayouts.size);
    shaderInfo.setPSetLayouts(setLayouts.data);

    /*
        VKAPI_ATTR VkResult VKAPI_CALL vkCreateShadersEXT(
            VkDevice                     device,
            uint32_t                     createInfoCount,
            const VkShaderCreateInfoEXT* pCreateInfos,
            const VkAllocationCallbacks* pAllocator,
            VkShaderEXT*                 pShaders);
    */
    vk::ShaderEXT shader;
    auto result = device.device.createShadersEXT(1, &shaderInfo,
        nullptr, &shader, dl);
    VkShaderEXT handle = shader;


    if (result == vk::Result::eSuccess) {
        logger->print("Successfully made compute shader");
        device.deletionQueue.push_back([logger, handle, dl](vk::Device device) {
            logger->print("deleted compute shader");
            device.destroyShaderEXT(handle, nullptr, dl);
        });
    }
    else {
        logger->print("Shader creation failed");
    }
    return shader;
}