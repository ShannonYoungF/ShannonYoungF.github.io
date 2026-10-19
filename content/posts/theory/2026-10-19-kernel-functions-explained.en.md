---
title: Understanding Kernel Functions Intuitively: From Matrices and Inner Products to Infinite-Dimensional Function Spaces
date: 2026-10-19
updated: 2026-10-19
category: theory
lang: en
translation_key: kernel-functions-explained
summary: Starting from matrix multiplication and inner products, this article builds an intuitive path toward integral kernels, function spaces, spectral decomposition, kernel methods, and neural operators.
tags: Kernel Functions, Function Spaces, Spectral Decomposition, Neural Operators
slug: kernel-functions-explained
---

## 1. What Is a Kernel Function?

Kernel functions appear throughout mathematics, machine learning, signal processing, and dynamical systems.

When we first encounter the term, we may see Gaussian kernels, convolution kernels, integral kernels, Green's function kernels, and heat kernels. Their mathematical forms and applications differ, but one important class of kernels shares a common idea: **describing how input at one location influences output at another.**

For example, consider an integral operator:

$$
v(x)=\int_\Omega k(x,y)u(y)\,dy
$$

Here:

- $u(y)$ is the input function;
- $v(x)$ is the output function;
- $k(x,y)$ is the kernel function, describing how the input at $y$ influences the output at $x$;
- $\Omega$ is the domain of integration.

For a fixed output location $x$, the kernel determines the contribution made by every location of the input function. Integration accumulates those contributions to produce the output value $v(x)$.

An integral kernel can therefore be understood intuitively as **a continuous influence-weight function**.

This is only an intuition for integral kernels, however, not a universal definition of every kind of kernel. A positive-definite kernel in machine learning, for example, is usually used to compute an inner product in a feature space and need not represent a physical influence.

## 2. Understanding Kernels Through Matrix Multiplication

The easiest route to an integral kernel begins with familiar matrix multiplication.

Suppose we have three inputs:

$$
\boldsymbol{u}=\begin{bmatrix}u_1\\u_2\\u_3\end{bmatrix}
$$

Applying a matrix $A$ gives the output:

$$
\boldsymbol{v}=A\boldsymbol{u}
$$

Expanding this expression:

$$
\begin{aligned}
v_1&=a_{11}u_1+a_{12}u_2+a_{13}u_3\\
v_2&=a_{21}u_1+a_{22}u_2+a_{23}u_3\\
v_3&=a_{31}u_1+a_{32}u_2+a_{33}u_3
\end{aligned}
$$

The entry $a_{ij}$ is the weight describing how the $j$-th input affects the $i$-th output. **Each row of the matrix specifies how all inputs contribute to one output.**

Now suppose the input is no longer three discrete values but a continuously varying function $u(y)$. A robot, for example, may receive a control input $u(t)$ throughout its motion. There is an input at every instant, and those inputs may jointly affect a future state.

We want to describe the influence of any input location $y$ on any output location $x$. The discrete matrix entry $a_{ij}$ then has a continuous analogue: the kernel $k(x,y)$.

The original matrix sum

$$
v_i=\sum_j a_{ij}u_j
$$

corresponds to the continuous integral

$$
v(x)=\int_\Omega k(x,y)u(y)\,dy
$$

Strictly speaking, numerical discretization must also account for quadrature weights. On a uniform grid, for example:

$$
a_{ij}\approx k(x_i,y_j)\Delta y
$$

Kernel values and matrix entries are therefore not always numerically identical. Their correspondence lies in the input-output relationship they describe.

**Matrix multiplication is a weighted sum over discrete inputs; a kernel integral is a weighted integral over continuous inputs.**

## 3. Why Call a Kernel a Continuous “Infinite-Dimensional Matrix”?

An ordinary matrix has finitely many rows and columns, such as $3\times3$ or $100\times100$.

A continuous function, by contrast, has a value at every point in its domain. We can therefore imagine $k(x,y)$ as a matrix with continuous row and column indices:

- $x$ identifies the output location, analogous to a row index;
- $y$ identifies the input location, analogous to a column index;
- $k(x,y)$ is the weight at that input-output pair.

From this perspective, an integral operator looks like a continuous form of matrix transformation.

This picture can lead to a common misunderstanding: **the fact that $x$ and $y$ can take infinitely many values does not make either variable infinite-dimensional.**

If $x\in[0,1]$, the interval contains infinitely many real numbers, but $x$ is still a one-dimensional variable. The true infinite dimensionality comes from the function space.

Consider the expansion

$$
u(x)=\sum_{n=1}^{\infty}c_n\phi_n(x)
$$

where $\phi_n(x)$ are basis functions and $c_n$ are expansion coefficients. Representing an arbitrary element of an infinite-dimensional function space generally requires infinitely many independent basis functions and coefficients.

We should therefore distinguish between:

- **the dimension of the independent variable**: how many independent coordinates specify one location;
- **the dimension of the function space**: how many independent basis directions are needed to specify one function.

A curve $u(x)$ has only one independent variable, while the space containing all such curves can still be infinite-dimensional.

**An integral kernel may represent an infinite-dimensional linear operator in continuous coordinates. This does not mean that the kernel's two arguments are themselves infinite-dimensional variables.**

## 4. Why Does a Kernel Not Automatically Remove Infinite Dimensionality?

If a kernel replaces the weights of a discrete matrix, does it turn an infinite-dimensional problem into a finite-dimensional one? No.

Consider again:

$$
v(x)=\int_\Omega k(x,y)u(y)\,dy
$$

Although we have written only one function of two variables, $k(x,y)$ must still describe relationships between locations across a continuous domain. The kernel itself may therefore contain infinitely many degrees of freedom.

Its value is not that it automatically reduces dimension. Rather, **it converts an abstract mapping between functions into a weighted integral with explicit structure.**

This representation lets us use integration theory, spectral theory, Fourier analysis, and numerical methods to study the operator.

Suppose, for example, that the kernel is translation-invariant:

$$
k(x,y)=k(x-y)
$$

On an appropriate domain, the integral operator then takes the form of a convolution:

$$
v(x)=(k*u)(x)
$$

By the convolution theorem:

$$
\mathcal F(v)=\mathcal F(k)\mathcal F(u)
$$

The integral in physical space becomes multiplication in Fourier space. This is one of the key mathematical ideas behind frequency-domain computation in the Fourier Neural Operator (FNO).

**A kernel does not necessarily reduce the dimension of a problem, but special structure in a kernel can make the computation dramatically simpler.**

## 5. How Do Kernels Relate to Inner Products, Orthogonality, and Basis Functions?

A kernel is not an isolated concept. It is deeply connected to inner products, orthogonality, and basis expansions from linear algebra.

### 5.1 Inner Products: Measuring Relationships Between Objects

In a finite-dimensional vector space, the inner product is

$$
\langle\boldsymbol a,\boldsymbol b\rangle=\sum_{i=1}^{n}a_ib_i
$$

For real-valued square-integrable functions, we can define

$$
\langle f,g\rangle=\int_\Omega f(x)g(x)\,dx
$$

The discrete sum in a vector inner product thus extends naturally to the continuous integral in a function inner product. An inner product not only expresses a geometric relationship between two objects; it also computes the projection of a function onto a particular direction.

### 5.2 Orthogonality: Separating Independent Components

Suppose a collection of basis functions satisfies

$$
\langle\phi_i,\phi_j\rangle=\delta_{ij}
$$

Then it forms an orthonormal system. If the system is complete, a function can be expanded as

$$
f(x)=\sum_{n=1}^{\infty}c_n\phi_n(x)
$$

with coefficients

$$
c_n=\langle f,\phi_n\rangle
$$

**Basis functions determine the representational directions, inner products compute the projection coefficients, and orthogonality allows different directions to be extracted independently.** Fourier series are a classic example of this idea.

### 5.3 A Kernel Integral as a Function Inner Product

Return to the integral operator

$$
v(x)=\int_\Omega k(x,y)u(y)\,dy
$$

For a fixed $x$, define

$$
k_x(y)=k(x,y)
$$

If $k_x$ and $u$ belong to the appropriate real-valued $L^2$ space, then

$$
v(x)=\langle k_x,u\rangle
$$

**Every output value of the integral operator can be viewed as the inner product of the input function with one kernel function.** As the output location $x$ changes, the corresponding function $k_x$ changes, producing the complete output function $v(x)$.

This inner-product interpretation of an integral kernel is related in form to the way a positive-definite kernel represents a feature-space inner product in a support vector machine, but the two are not identical mathematical definitions.

## 6. Kernels and Spectral Decomposition: Diagonalizing an Operator in Infinite Dimensions

In linear algebra, a real symmetric matrix admits an eigendecomposition:

$$
A=Q\Lambda Q^\mathsf T
$$

The central idea is to find special orthogonal directions along which the matrix transformation acts as simple scaling.

Similarly, for a suitable compact self-adjoint integral operator

$$
(\mathcal Ku)(x)=\int_\Omega k(x,y)u(y)\,dy
$$

we can write an eigenfunction expansion:

$$
\mathcal Ku=\sum_{n=1}^{\infty}\lambda_n\langle u,\phi_n\rangle\phi_n
$$

where:

- $\phi_n$ is an eigenfunction;
- $\lambda_n$ is an eigenvalue;
- $\langle u,\phi_n\rangle$ is the projection of the input function onto that eigenfunction.

This expression reveals how the integral operator works. First, project the input function onto the eigenfunction directions. Next, scale each component by its eigenvalue. Finally, recombine the components to form the output function.

Under suitable conditions, the kernel itself can also be expanded as

$$
k(x,y)=\sum_{n=1}^{\infty}\lambda_n\phi_n(x)\phi_n(y)
$$

Kernel functions, basis expansions, and spectral decomposition are therefore directly connected.

They can be understood as three views of the same linear operator:

- **Matrix representation** focuses on mappings between discrete coordinates.
- **Kernel-integral representation** focuses on interactions between continuous input and output locations.
- **Spectral representation** focuses on how the operator acts along eigenfunction directions.

The operator may be the same; only its representation changes.

## 7. What Are Some Common Kernel Functions?

There is no single, mutually exclusive taxonomy of kernels. Different fields emphasize different mathematical properties when they use the word “kernel.”

| Kernel | Typical form or property | Main applications |
|---|---|---|
| Gaussian kernel | Exponential decay with squared distance | Kernel regression, Gaussian processes |
| Exponential kernel | Exponential decay with temporal or spatial distance | Stochastic processes, dynamical modeling |
| Convolution kernel | $k(x-y)$ | Signal processing, CNNs, FNOs |
| Sinc kernel | $\sin(\omega_c r)/(\pi r)$ | Sampling theory, ideal low-pass filtering |
| Green's function kernel | Response kernel of a differential operator | Solving differential equations |
| Heat kernel | Fundamental solution describing heat diffusion | Diffusion processes, geometric analysis |
| Matérn kernel | Tunable smoothness of random functions | Gaussian processes, spatial statistics |
| Polynomial kernel | $(x^\mathsf Ty+c)^d$ | Kernel methods, feature maps |

Some of these kernels express similarity, some express a physical response, and others construct an integral operator.

Their common feature is not that they all represent physical influence. Rather, each uses a function with particular mathematical properties to encode relationships between objects or to define an operation.

## 8. How Do Kernels Relate to Neural Operators?

A neural operator aims to learn a mapping between function spaces:

$$
\mathcal G:u(\cdot)\mapsto v(\cdot)
$$

Ordinary neural networks mainly process finite-dimensional inputs and outputs. Neural operators instead focus on mappings from one function to another. Kernel functions are an important building block for some neural operators.

### 8.1 Fourier Neural Operator (FNO)

A typical integral-operator layer in an FNO can be written as

$$
(\mathcal K_\theta u)(x)=\int_\Omega\kappa_\theta(x,y)u(y)\,dy
$$

where $\kappa_\theta$ is a learnable kernel.

When an operator has convolutional structure, the Fourier transform can be used to compute it in the frequency domain.

The important idea behind an FNO is that **we do not have to evaluate a complicated integral directly in physical space; a frequency-domain representation can simplify the computation for operators with suitable structure.**

### 8.2 Deep Operator Network (DeepONet)

DeepONet uses a different representation:

$$
\mathcal G_\theta(u)(x)=\sum_{j=1}^{p}b_j(u)t_j(x)
$$

where:

- $b_j(u)$ is an input-dependent coefficient produced by the Branch Net;
- $t_j(x)$ is an output representation function produced by the Trunk Net.

This architecture has a clear formal resemblance to a basis expansion.

It constructs a mapping between function spaces by learning input-dependent coefficients and output representation functions, without requiring an explicit integral kernel.

Thus, **the FNO emphasizes kernel integration and Fourier representation, while DeepONet emphasizes function expansion and coefficient representation.** Their implementations differ, but both aim to learn complex mappings between functions.

## 9. Summary

The discussion above gives us a clear conceptual path:

$$
\boxed{\text{vector}\longrightarrow\text{function}\longrightarrow\text{function space}\longrightarrow\text{operator}\longrightarrow\text{kernel representation}}
$$

**First, vectors and functions.** A vector can be represented by finitely many coordinates, while a general function may require infinitely many basis coefficients. A function space can therefore be infinite-dimensional.

**Second, inner products and orthogonality.** Inner products define the geometry of a space, and an orthogonal basis decomposes a function into independent components.

**Third, matrices and operators.** A matrix describes a finite-dimensional linear map; an operator can describe a map between infinite-dimensional function spaces.

**Fourth, kernels and integral operators.** For operators that admit an ordinary integral-kernel representation, the kernel describes interactions between input and output locations, while integration performs the continuous weighted accumulation.

**Fifth, spectral decomposition and neural operators.** By choosing an appropriate representation of functions, a complex operator transformation can become a more tractable computation over coefficients.

The essence of an integral kernel can be summarized in one sentence:

> **A matrix uses discrete weights to describe relationships among finitely many inputs and outputs, while an integral kernel uses continuous weights to describe relationships among locations of functions. It does not eliminate infinite dimensionality; it gives certain infinite-dimensional linear maps a clear, analyzable, and computable representation.**

Seen this way, a kernel is no longer just a formula to memorize. It becomes an important bridge connecting linear algebra, function spaces, integral equations, differential equations, Fourier analysis, and the theory of neural operators.
