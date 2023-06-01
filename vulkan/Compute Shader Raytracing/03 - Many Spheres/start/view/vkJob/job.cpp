#include "job.h"

vkJob::MakeModel::MakeModel(vkMesh::ObjMesh& mesh, const char* objFilepath, const char* mtlFilepath, glm::mat4 preTransform):
mesh(mesh) {
	this->objFilepath = objFilepath;
	this->mtlFilepath = mtlFilepath;
	this->preTransform = preTransform;
}

void vkJob::MakeModel::execute(vk::CommandBuffer commandBuffer, vk::Queue queue) {
	mesh.load(objFilepath, mtlFilepath, preTransform);
	status = JobStatus::COMPLETE;
}

void vkJob::WorkQueue::add(Job* job) {

	if (length == 0) {
		first = job;
		last = job;
	}
	else {
		last->next = job;
		last = job;
	}

	length += 1;
}

vkJob::Job* vkJob::WorkQueue::get_next() {

	if (length == 0) {
		return nullptr;
	}

	Job* current = first;
	while (current) {
		if (current->status == JobStatus::PENDING) {
			return current;
		}

		current = current->next;
	}

	return nullptr;
}

void vkJob::WorkQueue::clear() {

	if (length == 0) {
		return;
	}

	Job* current = first;
	while (current) {

		Job* previous = current;
		current = current->next;
		delete previous;

	}

	length = 0;

}