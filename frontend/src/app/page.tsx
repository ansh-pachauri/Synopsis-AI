import LoginButton from "../components/react-common/loginButton";

export default function Home() {
  return (
    <div className="flex flex-col bg-black justify-center">
      <h1 className="text-4xl font-bold text-center text-zinc-900 dark:text-zinc-50">
        NeuroMesh
      </h1>
      <p className="text-lg text-center text-zinc-600 dark:text-zinc-400">
        AI-Powered Research Assistant
      </p>

      {/* Login Button */}
      <LoginButton/>
    </div>
  );
}
