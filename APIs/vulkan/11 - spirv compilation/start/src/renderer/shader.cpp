#include "shader.h"
#include "../logging/logger.h"
#include "../backend/file.h"
#include <vector>
#include <shaderc/shaderc.hpp>

/**
* @brief Generic bundle for shaderc compilation operations
*
*/
struct CompilationInfo {
    /**
    * @brief name of the original file, good for getting meaningful debug messages
    *
    */
    const char* fileName;

    /**
    * @brief kind type of shader to ultimately be produced
    *
    */
    shaderc_shader_kind kind;

    /**
    * @brief the source code
    *
    */
    std::vector<char> source;

    /**
    * @brief compilation options
    */
    shaderc::CompileOptions options;
};

/**
* @brief preprocess GLSL shader source code
* 
*/
void preprocess_shader(CompilationInfo& info) {

    //setup

    //compile

    //copy result into info for next compilation operation

    //Log output for fun
}

/**
* @brief Compile glsl source code to SPIR - V assembly.
* 
*/ 
void compile_file_to_assembly(CompilationInfo& info) {

    //setup

    //compile

    //copy result into info for next compilation operation

    //Log output for fun
}

/**
* @brief Compiles SPIR - V assembly to a SPIR-V binary
* 
* @return the SPIR-V binary code as a buffer of 32 bit words
*
*/
std::vector<uint32_t> compile_file(CompilationInfo& info) {

    //setup

    //compile

    //copy result to the final output

    //Log output for fun
}

std::vector<vk::ShaderEXT> make_shader_objects(vk::Device logicalDevice, 
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

    //Compile vertex module

    vk::ShaderCodeTypeEXT codeType = vk::ShaderCodeTypeEXT::eSpirv;
    const char* pName = "main";

    vk::ShaderCreateInfoEXT vertexInfo = {};
    vertexInfo.setFlags(flags);
    vertexInfo.setStage(vk::ShaderStageFlagBits::eVertex);
    vertexInfo.setNextStage(nextStage);
    vertexInfo.setCodeType(codeType);
    vertexInfo.setCodeSize(sizeof(uint32_t) * vertexCode.size());
    vertexInfo.setPCode(vertexCode.data());
    vertexInfo.setPName(pName);

    //Compile fragment module

    vk::ShaderCreateInfoEXT fragmentInfo = {};
    fragmentInfo.setFlags(flags);
    fragmentInfo.setStage(vk::ShaderStageFlagBits::eFragment);
    fragmentInfo.setCodeType(codeType);
    fragmentInfo.setCodeSize(sizeof(uint32_t) * fragmentCode.size());
    fragmentInfo.setPCode(fragmentCode.data());
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