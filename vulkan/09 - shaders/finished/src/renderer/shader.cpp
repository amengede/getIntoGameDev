#include "shader.h"
#include "../logging/logger.h"
#include "../backend/file.h"
#include <vector>

std::vector<vk::ShaderEXT> make_shader_objects(vk::Device logicalDevice, 
    const char* vertexFilename, const char* fragmentFilename, vk::DispatchLoaderDynamic& dl,
    std::deque<std::function<void(vk::Device)>>& deviceDeletionQueue) {

    Logger* logger = Logger::get_logger();

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

    std::vector<char> vertexSrc = read_file(vertexFilename);
    vk::ShaderCodeTypeEXT codeType = vk::ShaderCodeTypeEXT::eSpirv;
    const char* pName = "main";

    vk::ShaderCreateInfoEXT vertexInfo = {};
    vertexInfo.setFlags(flags);
    vertexInfo.setStage(vk::ShaderStageFlagBits::eVertex);
    vertexInfo.setNextStage(nextStage);
    vertexInfo.setCodeType(codeType);
    vertexInfo.setCodeSize(vertexSrc.size());
    vertexInfo.setPCode(vertexSrc.data());
    vertexInfo.setPName(pName);

    std::vector<char> fragmentSrc = read_file(fragmentFilename);
    vk::ShaderCreateInfoEXT fragmentInfo = {};
    fragmentInfo.setFlags(flags);
    fragmentInfo.setStage(vk::ShaderStageFlagBits::eFragment);
    fragmentInfo.setCodeType(codeType);
    fragmentInfo.setCodeSize(fragmentSrc.size());
    fragmentInfo.setPCode(fragmentSrc.data());
    fragmentInfo.setPName(pName);

    /*
        VKAPI_ATTR VkResult VKAPI_CALL vkCreateShadersEXT(
            VkDevice                     device,
            uint32_t                     createInfoCount,
            const VkShaderCreateInfoEXT* pCreateInfos,
            const VkAllocationCallbacks* pAllocator,
            VkShaderEXT*                 pShaders);
    */
    std::vector<vk::ShaderCreateInfoEXT> shaderInfo;
    shaderInfo.push_back(vertexInfo);
    shaderInfo.push_back(fragmentInfo);

    auto result = logicalDevice.createShadersEXT(shaderInfo, nullptr, dl);
    std::vector<vk::ShaderEXT> shaders;
    
    if (result.result == vk::Result::eSuccess) {
        logger->print("Successfully made shaders");
        shaders = result.value;
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