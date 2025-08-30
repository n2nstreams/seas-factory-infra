1. AI-Driven Dev Template
4:40
developmentdriven framework. And in this step, we're going to focus strictly on templates. And this is my favorite
4:47
section out of all of them. So, I'm so excited for you guys to see this in action. And what we're going to do, quick overview. First, we're going to
4:52
dive into how most developers are using cursor and some of the limitations. Then I'm going to dive into how you should be
4:59
using templates inside of cursor so you get an insane amount of leverage and way better results when using cursor. And
5:05
then finally, we're going to hop over to cursor so you can actually see this in action and see the power of using
5:11
templates inside of your AI development driven life cycle. So let's dive in. So first things first, when it comes to the
5:18
current development life cycle, this is what I see most developers do. Most developers go, "Hey, cursor, I would
5:24
like you to add a new page that has a chat window in it." So then cursor is
5:29
going to go, "Okay, cool. Well, I think I know what a chat window is. Maybe you provided a screenshot of what you
5:36
wanted." And cursor is just going to go, "Okay, cool. I'm going to start just make new page. Once I have the page, add
5:41
components. Once I have components, make them functional. Maybe talk to a database. Add packages." And it's just
5:47
going to go and do as much as it possibly can. Now, sometimes this does work great. Usually, the smaller the
5:52
task, the better it does. The bigger the task, it usually kind of varies in results. So, if you've ever experienced
5:58
cursor, you know, maybe not using your existing dependencies and just adding all sorts of new stuff and you're like,
6:03
"Hey, why the heck did AI go rogue on me?" It's usually one of the main issues of just not giving AI enough context.
6:11
Then the other issue is if sometimes for whatever reason you're like, "Hey, I told you to add this new feature. I had
6:17
an entire utils library with 30 functions to help with all things AI
6:23
chat related for the new page you're building and you skipped all of them and created new functions. So, you know, there's another common error that you'll
6:30
usually see AI agents make. So, that's because we're not providing context to
6:35
our AI agents and because we're not giving them enough context, they usually don't give us the best results. So, the
6:40
core lesson here is when you give AI context, it does great. when you don't eh sometimes it it usually it usually
6:46
breaks. So those are the few core errors that I usually see with the current development life cycle that developers
6:52
have when they're just saying hey go build this hey go add this. The other core issue that I see with the current
6:58
development life cycle for developers is they have zero leverage. What I mean by that is in the development life cycle
7:04
there's a few core things that we're always doing. We're always adding new features. We're always debugging issues, updating the UI, making git commits. And
7:11
there's a few core things that we're doing over and over and over and over again. And the problem is every time they're using cursor to do one of these
7:17
tasks, they're always starting from ground zero. And because they're starting from ground zero, you know, maybe on the last chat session inside of
7:24
cursor, they finally got it working perfectly. It was understanding their wants, their needs in the codebase, but
7:30
then when they hop to that new chat session, they're starting from ground zero again. And it's like once again just doesn't understand all the
7:36
components and all the files that you have inside your project. and you get back to those initial issues of hey it's
7:42
not going to implement the proper solutions. It's might not actually use your existing codebase and you just end
7:48
up with bad results. So this is the problems that I see with the current development life cycle. So now that
7:54
we've seen some of the problems, let me show you how you can improve this process to get way more leverage and 10
8:00
times better results. So let's dive into it. So here is what the updated life cycle looks like using AIdriven
8:07
development. Obviously, the main changes you see here are we are using templates and task and these new elements are
8:13
going to help us write way better code and get better results. So, let me explain each one of these first, how we
8:18
can build them and how they all get used together. So, a template is nothing more than a set of instructions on how we
8:25
want to do things. So, we're going to have a template saying how to create new features, how we debug things, what
8:31
we're trying to do when we improve the UI. So basically a template is going to be our mental model where we kind of
8:37
codify everything in our head for our development life cycle for how we perform each one of these tasks. Then
8:42
the template is going to generate a task document. A task document contains all
8:48
the core instructions AI needs to go implement the task or to go solve the
8:53
bug or do whatever we're trying to do. So basically we create templates. Once we have a template created, this
8:59
template will create a task and then we just pass that task in to cursor and say, "Hey, go fix and work on this
9:06
task." And then cursor will start writing the code. Now, why is this different? Well, we are going to make
9:12
sure that our templates have all the perfect instructions for like, hey, here's how the codebase is set up.
9:18
Here's how we usually go through everything step by step to build features. Here's how we handle working with the databases. Like, it's going to
9:24
contain all of our core instructions for our project. And that way once this template is generating the task, the
9:31
task itself is going to be a really long file that contains like, hey, here's the goal that the user trying to accomplish.
9:37
Here is exactly what success looks like. Hey, also by the way, when you're updating the front end, there's a bunch
9:42
of utility files that they've already made. I've already found them when I was searching through the codebase and understanding it all. So, you definitely
9:49
want to reuse these as much as you can. And then once we have context, our context set up properly inside this task
9:56
document. Once AI starts to update the code, it's just going to hum. It's going to do everything perfectly because it
10:03
already knows everything it needs to do because it was already predefined and listed out inside of this test document.
10:09
If you've experienced Cairo at all from AWS, it's very similar to that except
10:15
we're in control where we get to define our way for creating features, our way for debugging, our way for doing
10:21
everything. And you know, you can do it yourself. So you don't have to basically work with Cairo. You can do it inside cursor, which I love way more than
10:28
Cairo. So let's talk about how you actually do this. When you're using cursor, you can say, "Hey, cursor, I'm
10:33
trying to create a template. This template is going to help me create all new features for going forward." do your
10:40
best job. Look at my entire codebase. Point out all the most important things and then help me make this template.
10:45
Once you have the template, you're going to say, "All right, cursor. Thank you for making that template. I want to make a new page inside of my website for
10:52
handling chatting with Verscell AI SDK. Go make a task." Cursor is going to use
10:57
the template. Once it has the template, it's going to create the task. The task is going to have instructions on make
11:02
this component, make this component, do this, talk to this backend service. But usually when you're first creating
11:08
templates, it's going to be garbage. So then we go, "Oh, okay. Hey, cursor, do you see how in the task you said to do
11:14
all these three things?" That's completely wrong. Never do that again. You should always make sure that you
11:20
check this file over here to make sure that we're properly using our database schema. So then cursor is going to go,
11:27
okay, cool. I'm going to go update the template so that I never make this mistake again going forward. And then
11:32
I'm going to regenerate a new task. Then it's going to go and show the updated task. And we're going to go, okay, cool.
11:39
It looks like you are doing a really good job now at creating the new page for our AI chat interface. Oh, but you
11:45
did make one small mistake when you were creating the components. It looks like you weren't handling light mode and dark
11:50
mode, and you didn't make it mobile responsive. Can you update the template again? Once again, cursor will update the template and regenerate a new task.
11:58
And this is just going to happen over and over and over again. And eventually this tasks document right here is going
12:04
to become flawless at creating new task. And the reason why is because we've been consistently training it on its own
12:10
errors. Like we're not manually typing anything. We're having AI see what it did wrong and then improve it. See what
12:16
it did wrong and improve it. Then eventually what's going to happen going forward is every time you want to fix a new thing in your application, you just
12:22
say, "Hey, use the new feature template right here. Make a new task." That task
12:27
is going to be 99% perfect. Once the task is created, we just say, "All right, cursor, go update the code using
12:33
this task, and it's just going to do it perfectly." So that's it hypothetically. And you're going to be doing this for
12:39
every single development life cycle part that you work on as a developer. And
12:44
eventually, you're going to end up with a set of templates that allow you to just build, you know, at lightning fast speeds and produce high quality code. So
12:52
