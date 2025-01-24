#include "shader.h"
#include "../logging/logger.h"
#include "../backend/file.h"
#include <vector>
#include <shaderc/shaderc.hpp>
#include <sstream>

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
    Logger* logger = Logger::get_logger();
    shaderc::Compiler compiler;

    //compile
    shaderc::PreprocessedSourceCompilationResult result =
        compiler.PreprocessGlsl(info.source.data(), info.source.size(), info.kind, info.fileName, info.options);
    if (result.GetCompilationStatus() != shaderc_compilation_status_success) {
        logger->print(result.GetErrorMessage());
    }

    //copy result into info for next compilation operation
    const char* src = result.cbegin();
    size_t newSize = result.cend() - src;
    info.source.resize(newSize);
    memcpy(info.source.data(), src, newSize);

    //Log output for fun
    logger->print("---- Preprocessed GLSL source code ----");
    std::string output = { info.source.data(), info.source.data() + info.source.size() };
    logger->print(output);
}

/**
* @brief Compile glsl source code to SPIR - V assembly.
* 
*/ 
void compile_file_to_assembly(CompilationInfo& info) {

    //setup
    Logger* logger = Logger::get_logger();
    shaderc::Compiler compiler;

    //compile
    shaderc::AssemblyCompilationResult result = compiler.CompileGlslToSpvAssembly(
        info.source.data(), info.source.size(), info.kind, info.fileName, info.options);
    if (result.GetCompilationStatus() != shaderc_compilation_status_success) {
        logger->print(result.GetErrorMessage());
    }

    //copy result into info for next compilation operation
    const char* src = result.cbegin();
    size_t newSize = result.cend() - src;
    info.source.resize(newSize);
    memcpy(info.source.data(), src, newSize);

    //Log output for fun
    logger->print("---- SPIR-V Assembly code ----");
    std::string output = { info.source.data(), info.source.data() + info.source.size() };
    logger->print(output);
}

/**
* @brief Compiles SPIR - V assembly to a SPIR-V binary
* 
* @return the SPIR-V binary code as a buffer of 32 bit words
*
*/
std::vector<uint32_t> compile_file(CompilationInfo& info) {

    //setup
    Logger* logger = Logger::get_logger();
    shaderc::Compiler compiler;

    //compile
    shaderc::SpvCompilationResult module = compiler.AssembleToSpv(info.source.data(), info.source.size(), info.options);
    if (module.GetCompilationStatus() != shaderc_compilation_status_success) {
        logger->print("---- Assembly to Binary Compilation ----");
        logger->print(module.GetErrorMessage());
    }

    //copy result to the final output
    const uint32_t* src = module.cbegin();
    size_t wordCount = module.cend() - src;
    std::vector<uint32_t> output(wordCount);
    memcpy(output.data(), src, wordCount * sizeof(uint32_t));

    //Log output for fun
    logger->print("---- SPIR-V Binary Code ----");
    logger->print("Magic Number: ");
    std::stringstream converter;
    converter << output[0];
    logger->print(converter.str());

    return output;
}

std::vector<vk::ShaderEXT> make_shader_objects(vk::Device logicalDevice, 
    const char* name, vk::DispatchLoaderDynamic& dl,
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
    CompilationInfo info;
    info.fileName = filename.c_str();
    info.kind = shaderc_vertex_shader;
    info.source = read_file(info.fileName);
    info.options.SetTargetEnvironment(shaderc_target_env_opengl, shaderc_env_version_opengl_4_5);
    info.options.SetTargetEnvironment(shaderc_target_env_vulkan, shaderc_env_version_vulkan_1_3);
    info.options.SetSourceLanguage(shaderc_source_language_glsl);
    info.options.SetTargetSpirv(shaderc_spirv_version_1_6);
    info.options.SetOptimizationLevel(shaderc_optimization_level_performance);
    preprocess_shader(info);
    compile_file_to_assembly(info);
    std::vector<uint32_t> vertexCode = compile_file(info);

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

    filenameBuilder << "shaders/" << name << ".frag";
    filename = filenameBuilder.str();
    filenameBuilder.str("");
    info.fileName = filename.c_str();
    info.kind = shaderc_fragment_shader;
    info.source = read_file(info.fileName);
    preprocess_shader(info);
    compile_file_to_assembly(info);
    std::vector<uint32_t> fragmentCode = compile_file(info);

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