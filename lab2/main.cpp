#include <GLFW/glfw3.h>
#include <iostream>

int main() {
  if(!glfwInit()) {
    std::cerr << "Failed to initialize GLFW" << std::endl;
    return -1;
  }

  glfwDefaultWindowHints();

  GLFWwindow* window = glfwCreateWindow(300, 300, "Red Triangle", NULL, NULL);
  if(window == NULL) {
    std::cerr << "Failed to open GLFW window" << std::endl;
    glfwTerminate();
    return -1;
  }

  glfwMakeContextCurrent(window);

  while(glfwWindowShouldClose(window) == GL_FALSE) {
    glClear(GL_COLOR_BUFFER_BIT);
    glLoadIdentity();
    glColor4f(1, 0, 0, 1);
    glBegin(GL_TRIANGLES);
    glVertex3f( 0.0,  0.5, 0);
    glVertex3f( 0.5, -0.5, 0);
    glVertex3f(-0.5, -0.5, 0);
    glEnd();

    glfwSwapBuffers(window);
    glfwPollEvents();
  }

  glfwDestroyWindow(window);
  glfwTerminate();
  return 0;
}
