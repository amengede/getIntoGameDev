#pragma once
#include <vector>
#include <array>
#include <vulkan/vulkan.h>
#include <optional>
#include <deque>
#include <functional>
#include <glm/glm.hpp>
#include "vk_types.h"
#include "view/vk_mesh.h"
#include "scene.h"

/*------------------- variables ----------------------*/

const uint32_t WIDTH = 800;
const uint32_t HEIGHT = 600;
const int MAX_FRAMES_IN_FLIGHT{ 2 };

const std::vector<const char*> validationLayers = {
	"VK_LAYER_KHRONOS_validation"
};

const std::vector<const char*> deviceExtensions = {
	VK_KHR_SWAPCHAIN_EXTENSION_NAME
};

#ifdef NDEBUG
const bool enableValidationLayers{ false };
#else
const bool enableValidationLayers{ true };
#endif

/*------------------- structs          ---------------*/

struct QueueFamilyIndices {
	std::optional<uint32_t> graphicsFamily;
	std::optional<uint32_t> presentFamily;

	bool isComplete() {
		return graphicsFamily.has_value() &&
			presentFamily.has_value();
	}
};

struct SwapchainSupportDetails {
	// no of images supported, and width/height
	VkSurfaceCapabilitiesKHR capabilities;
	//supported pixel format
	std::vector<VkSurfaceFormatKHR> formats;
	std::vector<VkPresentModeKHR> presentModes;
};

struct UniformBufferObject {
	glm::mat4 view;
	glm::mat4 proj;
};

struct DeletionQueue {
	std::deque<std::function<void()>> deletors;

	void push_function(std::function<void()>&& function) {
		deletors.push_back(function);
	}

	void flush() {
		for (auto it = deletors.rbegin(); it != deletors.rend(); it++) {
			(*it)();
		}

		deletors.clear();
	}
};

struct MeshPushConstants {
	glm::mat4 model;
};

/*------------------- classes          ---------------*/

class VulkanEngine {
public:

	/*------------------- variables ------------------*/
#pragma region
	struct GLFWwindow* window;
	VkPhysicalDevice physicalDevice{ VK_NULL_HANDLE };
	VkDevice device;
	VkInstance instance;
	VkDebugUtilsMessengerEXT debugMessenger;
	VkSurfaceKHR surface;
	VkQueue graphicsQueue;
	VkQueue presentQueue;
	VkSwapchainKHR swapchain;
	std::vector<VkImage> swapchainImages;
	VkFormat swapchainImageFormat;
	VkExtent2D swapchainExtent;
	std::vector<VkImageView> swapchainImageViews;
	VkRenderPass renderPass;
	VkPipelineLayout pipelineLayout;
	VkPipeline graphicsPipeline;
	std::vector<VkFramebuffer> swapchainFramebuffers;
	VkCommandPool commandPool;
	std::vector<VkCommandBuffer> commandBuffers;
	std::vector<VkSemaphore> imageAvailableSemaphores;
	std::vector<VkSemaphore> renderFinishedSemaphores;
	std::vector<VkFence> inFlightFences;
	std::vector<VkFence> imagesInFlight;
	size_t currentFrame{ 0 };
	bool resized{ false };
	VkDescriptorSetLayout descriptorSetLayout;
	std::vector<Buffer> uniformBuffers;
	VkDescriptorPool descriptorPool;
	std::vector<VkDescriptorSet> descriptorSets;
	Image textureImage;
	VkSampler textureSampler;
	Image depthImage;
	double lastTime;
	int frameCount{ 0 };
	VkSampleCountFlagBits msaaSamples;
	Image msColorImage;
	DeletionQueue mainDeletionQueue;

	Mesh statue;
	Mesh ground;
#pragma endregion
	/*------------------- initialisers ---------------*/
#pragma region

	void run();

	void initWindow();

	void initVulkan();

	void createInstance();

	void setupDebugMessenger();

	void createSurface();

	void loadModels();

	void createTextureImages();
#pragma endregion
	/*------------------- device functions -----------*/
#pragma region
	QueueFamilyIndices findQueueFamilies(VkPhysicalDevice device);

	void pickPhysicalDevice();

	bool checkDeviceExtensionSupport(VkPhysicalDevice device);

	bool isDeviceSuitable(VkPhysicalDevice device);

	void createLogicalDevice();

	VkSampleCountFlagBits getMaxSampleCount();
#pragma endregion
	/*------------------- swapchain ------------------*/
#pragma region
	SwapchainSupportDetails querySwapchainSupport(VkPhysicalDevice device);

	VkExtent2D chooseSwapchainExtent(const VkSurfaceCapabilitiesKHR& capabilities);

	VkSurfaceFormatKHR chooseSwapchainSurfaceFormat(const std::vector<VkSurfaceFormatKHR>& availableFormats);

	VkPresentModeKHR chooseSwapchainPresentMode(const std::vector<VkPresentModeKHR>& availablePresentModes);

	void createSwapchain();

	void createImageViews();

	void createFramebuffers();

	void recreateSwapchain();
#pragma endregion
	/*------------------- graphics pipeline ----------*/
#pragma region
	void createRenderPass();

	void createDescriptorSetLayout();

	void createDescriptorPool();

	void createDescriptorSets();

	void createGraphicsPipeline();

	VkShaderModule createShaderModule(const std::vector<char>& code);
#pragma endregion
	/*------------------- commands  ------------------*/
#pragma region
	void createCommandPool();

	void createSyncObjects();

	VkCommandBuffer beginSingleTimeCommands();

	void endSingleTimeCommands(VkCommandBuffer commandBuffer);
#pragma endregion
	/*------------------- buffers/memory management --*/
#pragma region
	void createVertexBuffer(Mesh& mesh);

	void createIndexBuffer(Mesh& mesh);

	void createUniformBuffers();

	void createBuffer(VkDeviceSize size, VkBufferUsageFlags usage,
		VkMemoryPropertyFlags properties, Buffer& buffer);

	void copyBuffer(Buffer& srcBuffer, Buffer& dstBuffer, VkDeviceSize size);

	uint32_t findMemoryType(uint32_t typeFilter, VkMemoryPropertyFlags properties);

	void transitionImageLayout(Image& image, VkFormat format,
		VkImageLayout oldLayout, VkImageLayout newLayout);

	void copyBufferToImage(Buffer& buffer, Image& image, uint32_t width, uint32_t height);

	void createTextureImageView();

	VkImageView createImageView(VkImage image, VkFormat format, VkImageAspectFlags aspect, uint32_t mipLevels);

	void createImage(uint32_t width, uint32_t height, VkSampleCountFlagBits samples, VkFormat format, VkImageTiling tiling,
		VkImageUsageFlags usage, VkMemoryPropertyFlags properties, Image& image);

	void createTextureSampler();

	void createColorResources();

	void createDepthResources();

	VkFormat findDepthFormat();

	VkFormat findSupportedFormat(const std::vector<VkFormat>& candidates, VkImageTiling tiling,
		VkFormatFeatureFlags features);

	void uploadToMemoryLocation(VkDeviceMemory dstMemory, const void* srcData, VkDeviceSize memorySize);
#pragma endregion
	/*------------------- main loop ------------------*/
#pragma region
	void drawFrame(Scene* scene);

	void updateUniformBuffer(uint32_t currentImage);

	void showFPS(GLFWwindow* pWindow);
#pragma endregion
	/*------------------- cleanup --------------------*/
#pragma region
	void cleanup();

	void cleanupSwapchain();

	void cleanupBuffer(Buffer& buffer);

	void cleanupImage(Image& image);

	void cleanupMesh(Mesh& mesh);
#pragma endregion
};