#include "image.h"

vk::ImageView create_image_view(
    vk::Device logicalDevice, vk::Image image, vk::Format format) {
    
    /*
    * ImageViewCreateInfo( VULKAN_HPP_NAMESPACE::ImageViewCreateFlags flags_ = {},
        VULKAN_HPP_NAMESPACE::Image                image_ = {},
        VULKAN_HPP_NAMESPACE::ImageViewType    viewType_  = VULKAN_HPP_NAMESPACE::ImageViewType::e1D,
        VULKAN_HPP_NAMESPACE::Format           format_    = VULKAN_HPP_NAMESPACE::Format::eUndefined,
        VULKAN_HPP_NAMESPACE::ComponentMapping components_            = {},
        VULKAN_HPP_NAMESPACE::ImageSubresourceRange subresourceRange_ = {} ) VULKAN_HPP_NOEXCEPT
        : flags( flags_ )
        , image( image_ )
        , viewType( viewType_ )
        , format( format_ )
        , components( components_ )
        , subresourceRange( subresourceRange_ )
    */

    
}