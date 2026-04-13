import { Trophy, GitBranch, Timer, Brain, Bike } from 'lucide-react';
import { motion } from 'motion/react';

interface ResultProps {
  stats: { rounds: number; time: string };
  onRestart: () => void;
  onHome: () => void;
}

export default function Result({ stats, onRestart, onHome }: ResultProps) {
  return (
    <div className="space-y-16 pb-12">
      {/* Victory Banner */}
      <section className="text-center pt-8">
        <motion.div 
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          className="inline-flex items-center justify-center gap-3 bg-primary-container text-on-primary-container px-8 py-3 rounded-full mb-8"
        >
          <Trophy className="w-5 h-5 fill-current" />
          <span className="text-[10px] font-bold tracking-[0.2em] uppercase">挑战完成</span>
        </motion.div>
        <motion.h2 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="font-headline text-7xl md:text-9xl font-extrabold tracking-tighter text-primary mb-4"
        >
          胜利
        </motion.h2>
        <motion.p 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="font-body text-on-surface-variant text-lg max-w-sm mx-auto font-medium leading-relaxed"
        >
          以太向导对此印象深刻。你的直觉在未知中开辟了一条道路。
        </motion.p>
      </section>

      {/* Result Grid */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        {/* Target Word Card */}
        <motion.div 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          className="md:col-span-7 relative group overflow-hidden bg-surface-container-lowest rounded-[2.5rem] p-1.5 shadow-sm"
        >
          <div className="bg-surface rounded-[2rem] p-10 h-full flex flex-col justify-center relative overflow-hidden">
            <div className="absolute -right-16 -top-16 w-64 h-64 bg-primary/5 rounded-full blur-3xl" />
            <span className="text-on-surface-variant font-bold text-[10px] uppercase tracking-[0.3em] mb-6 block">正确答案：</span>
            <div className="flex items-baseline gap-4">
              <span className="font-headline text-6xl md:text-8xl font-bold text-on-surface tracking-tighter">BICYCLE</span>
            </div>
            <div className="mt-12 flex items-center text-primary/30">
              <Bike className="w-10 h-10" />
              <div className="ml-6 h-[1px] flex-grow bg-outline-variant/20" />
            </div>
          </div>
        </motion.div>

        {/* Stats Section */}
        <div className="md:col-span-5 grid grid-cols-2 gap-4">
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.4 }}
            className="bg-surface-container-low rounded-[2rem] p-8 flex flex-col justify-between"
          >
            <GitBranch className="w-8 h-8 text-secondary mb-6" />
            <div>
              <div className="font-headline text-4xl font-bold text-on-surface">{stats.rounds}</div>
              <div className="font-bold text-[9px] uppercase tracking-widest text-on-surface-variant mt-1">使用轮次</div>
            </div>
          </motion.div>
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.5 }}
            className="bg-surface-container-low rounded-[2rem] p-8 flex flex-col justify-between"
          >
            <Timer className="w-8 h-8 text-secondary mb-6" />
            <div>
              <div className="font-headline text-4xl font-bold text-on-surface">{stats.time}</div>
              <div className="font-bold text-[9px] uppercase tracking-widest text-on-surface-variant mt-1">总用时</div>
            </div>
          </motion.div>
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="col-span-2 glass-card rounded-[2rem] p-8 relative overflow-hidden"
          >
            <div className="relative z-10">
              <div className="flex justify-between items-end mb-6">
                <div>
                  <Brain className="w-6 h-6 text-tertiary mb-2 fill-current" />
                  <div className="font-bold text-[9px] uppercase tracking-widest text-on-surface-variant">AI 信心指数</div>
                </div>
                <div className="font-headline text-5xl font-bold text-tertiary">85%</div>
              </div>
              <div className="h-2.5 w-full bg-surface-variant/30 rounded-full overflow-hidden">
                <motion.div 
                  initial={{ width: 0 }}
                  animate={{ width: '85%' }}
                  transition={{ delay: 1, duration: 1.5, ease: "easeOut" }}
                  className="h-full bg-gradient-to-r from-tertiary to-tertiary-container rounded-full" 
                />
              </div>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Action Buttons */}
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
        className="flex flex-col md:flex-row gap-4 justify-center items-center"
      >
        <button 
          onClick={onRestart}
          className="w-full md:w-64 btn-primary-gradient font-headline font-bold py-6 rounded-2xl text-lg"
        >
          再玩一次
        </button>
        <button 
          onClick={onHome}
          className="w-full md:w-64 bg-secondary-container text-on-secondary-container font-headline font-bold py-6 rounded-2xl text-lg hover:opacity-80 transition-all active:scale-95"
        >
          返回首页
        </button>
      </motion.div>
    </div>
  );
}
