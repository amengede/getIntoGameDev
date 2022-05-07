#pragma once
#include <vector>
#include <array>
#include <vulkan/vulkan.h>
#include <optional>
#include <glm/glm.hpp>
#include "vk_types.h"
#include "view/vk_mesh.h"

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
	glm::mat4 model;
	glm::mat4 view;
	glm::mat4 proj;
};

/*------------------- classes          ---------------*/

class VulkanEngine {
public:
	void run();

	VkCommandBuffer beginSingleTimeCommands();

	void endSingleTimeCommands(VkCommandBuffer commandBuffer);

	void createBuffer(VkDeviceSize size, VkBufferUsageFlags usage,
		VkMemoryPropertyFlags properties, Buffer& buffer);

	void copyBuffer(Buffer& srcBuffer, Buffer& dstBuffer, VkDeviceSize size);

	uint32_t findMemoryType(uint32_t typeFilter, VkMemoryPropertyFlags properties);

	void transitionImageLayout(Image& image, VkFormat format,
		VkImageLayout oldLayout, VkImageLayout newLayout);

	void copyBufferToImage(Buffer& buffer, Image& image, uint32_t width, uint32_t height);

	VkImageView createImageView(VkImage image, VkFormat format, VkImageAspectFlags aspect, uint32_t mipLevels);

	void createImage(uint32_t width, uint32_t height, VkSampleCountFlagBits samples, VkFormat format, VkImageTiling tiling,
		VkImageUsageFlags usage, VkMemoryPropertyFlags properties, Image& image);

	void uploadToMemoryLocation(VkDeviceMemory dstMemory, const void* srcData, VkDeviceSize memorySize);

	void cleanupBuffer(Buffer& buffer);

	void cleanupImage(Image& image);

	void cleanupMesh(Mesh& mesh);

	VkPhysicalDevice physicalDevice{ VK_NULL_HANDLE };

private:
	/*------------------- variables ----------------------*/

	struct GLFWwindow* window;
	VkInstance instance;
	VkDebugUtilsMessengerEXT debugMessenger;
	VkSurfaceKHR surface;
	VkDevice device;
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
	Mesh statue;
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

	/*------------------- initialisers ---------------*/

	void initWindow();

	void initVulkan();

	void createInstance();

	void setupDebugMessenger();

	void createSurface();

	void loadModels();

	/*------------------- device functions -----------*/

	QueueFamilyIndices findQueueFamilies(VkPhysicalDevice device);

	void pickPhysicalDevice();

	bool checkDeviceExtensionSupport(VkPhysicalDevice device);

	bool isDeviceSuitable(VkPhysicalDevice device);

	void createLogicalDevice();

	VkSampleCountFlagBits getMaxSampleCount();

	/*------------------- swapchain ------------------*/

	SwapchainSupportDetails querySwapchainSupport(VkPhysicalDevice device);

	VkExtent2D chooseSwapchainExtent(const VkSurfaceCapabilitiesKHR& capabilities);

	VkSurfaceFormatKHR chooseSwapchainSurfaceFormat(const std::vector<VkSurfaceFormatKHR>& availableFormats);

	VkPresentModeKHR chooseSwapchainPresentMode(const std::vector<VkPresentModeKHR>& availablePresentModes);

	void createSwapchain();

	void createImageViews();

	void createFramebuffers();

	void recreateSwapchain();

	/*------------------- graphics pipeline ----------*/

	void createRenderPass();

	void createDescriptorSetLayout();

	void createDescriptorPool();

	void createDescriptorSets();

	void createGraphicsPipeline();

	VkShaderModule createShaderModule(const std::vector<char>& code);

	/*------------------- commands  ------------------*/

	void createCommandPool();

	void createCommandBuffers();

	void createSyncObjects();

	/*------------------- buffers/memory management --*/

	void createVertexBuffer();

	void createIndexBuffer();

	void createUniformBuffers();

	void createTextureImageView();

	void createTextureSampler();

	void createColorResources();

	void createDepthResources();

	VkFormat findDepthFormat();

	VkFormat findSupportedFormat(const std::vector<VkFormat>& candidates, VkImageTiling tiling,
		VkFormatFeatureFlags features);

	void createTextureImages();

	/*------------------- main loop ------------------*/

	void mainLoop();

	void drawFrame();

	void updateUniformBuffer(uint32_t currentImage);

	void showFPS(GLFWwindow* pWindow);

	/*------------------- cleanup --------------------*/

	void cleanup();

	void cleanupSwapchain();
};