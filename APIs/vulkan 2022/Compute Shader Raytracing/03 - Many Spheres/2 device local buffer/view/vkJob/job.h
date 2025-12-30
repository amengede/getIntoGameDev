#pragma once
#include "../../config.h"
#include "../vkMesh/obj_mesh.h"

namespace vkJob {

	enum class JobStatus {
		PENDING,
		IN_PROGRESS,
		COMPLETE
	};

	class Job {
	public:
		JobStatus status = JobStatus::PENDING;
		Job* next = nullptr;
		virtual void execute(vk::CommandBuffer commandBuffer, vk::Queue queue) = 0;
	};

	class MakeModel: public Job {
	public:
		const char* objFilepath;
		const char* mtlFilepath;
		glm::mat4 preTransform;
		vkMesh::ObjMesh& mesh;
		MakeModel(vkMesh::ObjMesh& mesh, const char* objFilepath, const char* mtlFilepath, glm::mat4 preTransform);
		virtual void execute(vk::CommandBuffer commandBuffer, vk::Queue queue) final;
	};

	class WorkQueue {
	public:
		Job* first = nullptr, * last = nullptr;
		size_t length = 0;
		void add(Job* job);
		Job* get_next();
		void clear();
	};
}